import React, { useEffect, useRef, useState } from 'react'
import { useGlobalStore } from '../store'
import { mapRenderer } from '../map/wrapper'
import { studyAreaRegistry } from '../services/studyArea'
import { logger } from '../utils/logger'
import { soilApi } from '../api/client'
import { Coordinate, SoilObservation, Command } from '../types'
import { eventBus } from '../utils/eventBus'
import { commandManager } from '../utils/commandBus'
import {
  ObservationSummary,
  ProfileSelector,
  LayerList,
  ScientificPropertyTable,
  ClassificationCard
} from '../components/ScientificPanelComponents'
import { SearchBox, NavigationControls, BookmarksPanel } from '../components/SearchAndNavigation'
import { LayerLegendPanel } from '../components/LayerLegendPanel'
import { Layers, Info, Menu, Undo, Redo } from 'lucide-react'

class SelectCoordinateCommand implements Command {
  id = 'SelectCoordinate'
  timestamp = Date.now()
  private previousProfileIndex: number
  private previousLayerIndex: number | null

  constructor(
    private coord: Coordinate,
    private previousCoord: Coordinate | null,
    private previousObs: SoilObservation | null,
    private selectFn: (coord: Coordinate | null, executeFetch: boolean) => Promise<void>
  ) {
    const store = useGlobalStore.getState()
    this.previousProfileIndex = store.activeProfileIndex
    this.previousLayerIndex = store.activeLayerIndex
  }

  async execute() {
    await this.selectFn(this.coord, true)
  }

  async undo() {
    await this.selectFn(this.previousCoord, false)
    const store = useGlobalStore.getState()
    store.setActiveObservation(this.previousObs)
    store.setActiveProfileIndex(this.previousProfileIndex)
    store.setActiveLayerIndex(this.previousLayerIndex)
  }
}

export const AppShell: React.FC = () => {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  
  const {
    isInitialized,
    setInitialized,
    center,
    zoom,
    sidebarOpen,
    toggleSidebar,
    setSidebarOpen,
    infoPanelOpen,
    setInfoPanelOpen,
    activeStudyArea,
    setActiveStudyArea,
    activeDatasetId,
    setActiveDatasetId,
    selectedCoordinate,
    setSelectedCoordinate,
    activeObservation,
    setActiveObservation,
    loading,
    setLoading,
    error,
    setError,
    basemap,
    setBasemap,
    activeProfileIndex,
    setActiveProfileIndex,
    activeLayerIndex,
    setActiveLayerIndex,
  } = useGlobalStore()

  // Local state for hover coordinates
  const [hoverCoord, setHoverCoord] = useState<Coordinate | null>(null)

  // Restore state from URL on initial mount
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlLat = parseFloat(params.get('lat') || '')
    const urlLon = parseFloat(params.get('lon') || '')
    const urlZoom = parseFloat(params.get('zoom') || '')

    const store = useGlobalStore.getState()

    if (!isNaN(urlLat) && !isNaN(urlLon)) {
      store.setCenter([urlLon, urlLat])
    }
    if (!isNaN(urlZoom)) {
      store.setZoom(urlZoom)
    }

    const selectedLat = parseFloat(params.get('selected_lat') || '')
    const selectedLon = parseFloat(params.get('selected_lon') || '')
    if (!isNaN(selectedLat) && !isNaN(selectedLon)) {
      const coord = { latitude: selectedLat, longitude: selectedLon }
      // Trigger geocoding query programmatically on mount once Map is ready
      const triggerInitialQuery = async () => {
        // Wait briefly for map/api clients to be ready
        await new Promise(resolve => setTimeout(resolve, 500))
        
        setSelectedCoordinate(coord)
        eventBus.dispatch('CoordinateSelected', coord)
        mapRenderer.setSelectionMarker(selectedLat, selectedLon)
        
        setInfoPanelOpen(true)
        setLoading(true)
        setError(null)
        try {
          const obs = await soilApi.getSoilObservation(coord)
          setActiveObservation(obs)
          eventBus.dispatch('ObservationLoaded', obs)
          setActiveProfileIndex(0)
          setActiveLayerIndex(null)
        } catch (err: any) {
          logger.error('Failed to restore soil observation from URL:', err)
          setError(err.message || 'Failed to restore soil observation')
          setActiveObservation(null)
          eventBus.dispatch('ObservationLoaded', null)
        } finally {
          setLoading(false)
        }
      }
      triggerInitialQuery()
    }
  }, [])

  // Synchronize URL with active map state
  useEffect(() => {
    const params = new URLSearchParams()
    // 1. Camera state
    params.set('lat', center[1].toFixed(5))
    params.set('lon', center[0].toFixed(5))
    params.set('zoom', zoom.toFixed(1))

    // 2. Selected Coordinate (if any)
    if (selectedCoordinate) {
      params.set('selected_lat', selectedCoordinate.latitude.toFixed(5))
      params.set('selected_lon', selectedCoordinate.longitude.toFixed(5))
    }

    const newUrl = `${window.location.pathname}?${params.toString()}`
    window.history.replaceState(null, '', newUrl)
  }, [center, zoom, selectedCoordinate])

  // Ref to hold the map click handler to avoid stale closures
  const clickHandlerRef = useRef<((e: any) => void) | null>(null)

  // Keep clickHandlerRef updated with latest logic
  useEffect(() => {
    clickHandlerRef.current = async (e: any) => {
      const coord = e.coordinate
      const store = useGlobalStore.getState()

      const cmd = new SelectCoordinateCommand(
        coord,
        store.selectedCoordinate,
        store.activeObservation,
        async (selectedCoord, executeFetch) => {
          setSelectedCoordinate(selectedCoord)
          if (selectedCoord) {
            eventBus.dispatch('CoordinateSelected', selectedCoord)
            if (executeFetch) {
              setInfoPanelOpen(true)
              setSidebarOpen(false)
              setLoading(true)
              setError(null)
              try {
                const obs = await soilApi.getSoilObservation(selectedCoord)
                setActiveObservation(obs)
                eventBus.dispatch('ObservationLoaded', obs)
                setActiveProfileIndex(0) // Reset tab index on successful fetch
                setActiveLayerIndex(null) // Reset active layer selection on new fetch
              } catch (err: any) {
                logger.error('Failed to retrieve soil observation:', err)
                setError(err.message || 'Failed to retrieve soil observation')
                setActiveObservation(null)
                eventBus.dispatch('ObservationLoaded', null)
              } finally {
                setLoading(false)
              }
            }
          } else {
            setActiveObservation(null)
          }
        }
      )

      commandManager.executeCommand(cmd)
    }
  })

  // Forward to refs to avoid recreating event listeners
  const moveEndHandlerRef = useRef<(() => void) | null>(null)
  useEffect(() => {
    moveEndHandlerRef.current = () => {
      const newCenter = mapRenderer.getCenter()
      const newZoom = mapRenderer.getZoom()
      if (newCenter) {
        useGlobalStore.getState().setCenter(newCenter)
      }
      if (newZoom !== null) {
        useGlobalStore.getState().setZoom(newZoom)
      }
    }
  })

  const mouseMoveHandlerRef = useRef<((e: any) => void) | null>(null)
  useEffect(() => {
    mouseMoveHandlerRef.current = (e: any) => {
      setHoverCoord(e.coordinate)
    }
  })

  // Initialize Map wrapper on shell mount
  useEffect(() => {
    if (mapContainerRef.current) {
      try {
        mapRenderer.initialize('map-canvas-container', {
          container: 'map-canvas-container',
          style: basemap, // Load the configured default basemap
          center: center,
          zoom: zoom,
          maxBounds: activeStudyArea.bounds, // Apply study area constraints
        })
        setInitialized(true)
        logger.info('Map wrapper initialized inside AppShell layout')

        // Register the map click event handler exactly once, forwarding to the ref
        mapRenderer.on('click', (e) => {
          if (clickHandlerRef.current) {
            clickHandlerRef.current(e)
          }
        })

        mapRenderer.on('moveend', () => {
          if (moveEndHandlerRef.current) {
            moveEndHandlerRef.current()
          }
        })

        mapRenderer.on('zoomend', () => {
          if (moveEndHandlerRef.current) {
            moveEndHandlerRef.current()
          }
        })

        mapRenderer.on('mousemove', (e) => {
          if (mouseMoveHandlerRef.current) {
            mouseMoveHandlerRef.current(e)
          }
        })
      } catch (err) {
        logger.error('AppShell failed to load Map engine:', err)
      }
    }

    return () => {
      mapRenderer.destroy()
      setInitialized(false)
      logger.info('Map wrapper destroyed on AppShell unmount')
    }
  }, [])

  // Manage selection indicator marker
  useEffect(() => {
    if (isInitialized) {
      if (selectedCoordinate) {
        mapRenderer.setSelectionMarker(selectedCoordinate.latitude, selectedCoordinate.longitude)
      } else {
        mapRenderer.setSelectionMarker(null, null)
      }
    }
  }, [selectedCoordinate, isInitialized])

  // Manage cursor feedback depending on loading state
  useEffect(() => {
    if (isInitialized) {
      mapRenderer.setCursor(loading ? 'wait' : 'pointer')
    }
  }, [loading, isInitialized])

  // Trigger map resize when sidebar or info panel open/close state changes
  useEffect(() => {
    if (isInitialized) {
      mapRenderer.resize()
      // Resize again after CSS transition duration (300ms) completes
      const timer = setTimeout(() => {
        mapRenderer.resize()
      }, 310)
      return () => clearTimeout(timer)
    }
  }, [sidebarOpen, infoPanelOpen, isInitialized])

  // Synchronize thematic overlays to Map renderer
  const overlays = useGlobalStore((state) => state.overlays)
  useEffect(() => {
    if (isInitialized) {
      overlays.forEach((layer) => {
        try {
          mapRenderer.addLayer(layer)
          mapRenderer.updateLayer(layer.id, {
            visible: layer.visible,
            opacity: layer.opacity,
          })
        } catch (err) {
          logger.warn(`Failed to sync layer ${layer.id}:`, err)
        }
      })
    }
  }, [overlays, isInitialized])

  const handleStudyAreaChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const areaId = e.target.value
    const area = studyAreaRegistry.get(areaId)
    setActiveStudyArea(area)
    eventBus.dispatch('StudyAreaChanged', area)

    // Update basemap to first available basemap of new study area
    const defaultBm = area.availableBasemaps[0] || 'satellite'
    setBasemap(defaultBm)
    mapRenderer.setBasemapStyle(defaultBm)
    eventBus.dispatch('BasemapChanged', defaultBm)

    // Apply constraints of the new study area:
    mapRenderer.setMaxBounds(area.bounds)

    const lat = (area.bounds[0][1] + area.bounds[1][1]) / 2
    const lon = (area.bounds[0][0] + area.bounds[1][0]) / 2
    mapRenderer.setCenter(lat, lon)
    mapRenderer.setZoom(area.defaultZoom)
  }

  const handleDatasetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const ds = e.target.value
    setActiveDatasetId(ds)
    eventBus.dispatch('DatasetChanged', ds)
  }

  const handleBasemapChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const bm = e.target.value
    setBasemap(bm)
    mapRenderer.setBasemapStyle(bm)
    eventBus.dispatch('BasemapChanged', bm)
  }

  // Render method for the Scientific Profile Panel based on state
  const renderScientificProfile = () => {
    // 1. Initial State (No coordinate selected)
    if (!selectedCoordinate) {
      return (
        <div className="flex-1 p-5 text-theme-text-sec text-xs flex flex-col gap-4 overflow-y-auto font-sans leading-relaxed select-none">
          <div className="flex flex-col gap-1.5 pb-3 border-b border-theme-border">
            <h3 className="text-sm font-bold text-theme-text bg-gradient-to-r from-teal-500 to-cyan-500 dark:from-teal-400 dark:to-cyan-400 bg-clip-text text-transparent">
              Welcome to Global Soil Explorer
            </h3>
            <p className="text-[11px] text-theme-text-muted">
              An open-source Web GIS platform for exploring soil datasets and scientific characteristics.
            </p>
          </div>

          <div className="flex flex-col gap-3">
            <span className="text-[10px] font-bold text-theme-text-muted uppercase tracking-wider">How to get started:</span>
            
            <div className="flex gap-2.5 items-start p-2.5 rounded-xl bg-theme-card border border-theme-border">
              <div className="flex items-center justify-center w-5 h-5 rounded-full bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/30 font-bold font-mono text-[10px] shrink-0 mt-0.5">
                1
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="font-semibold text-theme-text">Select a Location</span>
                <span className="text-[11px] text-theme-text-sec">Click any point on the map, or use the search bar in the top-left to look up coordinates or place names.</span>
              </div>
            </div>

            <div className="flex gap-2.5 items-start p-2.5 rounded-xl bg-theme-card border border-theme-border">
              <div className="flex items-center justify-center w-5 h-5 rounded-full bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/30 font-bold font-mono text-[10px] shrink-0 mt-0.5">
                2
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="font-semibold text-theme-text">View Soil Horizons</span>
                <span className="text-[11px] text-theme-text-sec">Soil profiles are split into depth layers (horizons). Click a horizon card to reveal chemical and physical properties.</span>
              </div>
            </div>

            <div className="flex gap-2.5 items-start p-2.5 rounded-xl bg-theme-card border border-theme-border">
              <div className="flex items-center justify-center w-5 h-5 rounded-full bg-teal-500/10 text-teal-600 dark:text-teal-400 border border-teal-500/30 font-bold font-mono text-[10px] shrink-0 mt-0.5">
                3
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="font-semibold text-theme-text">Explore Interactive Glossary</span>
                <span className="text-[11px] text-theme-text-sec">Click on any soil measurement (like pH, Organic Carbon, or Base Saturation) in the properties table to view its definition.</span>
              </div>
            </div>
          </div>

          <div className="mt-2 p-3 rounded-xl border border-theme-border bg-theme-btn-bg/35 text-[11px] text-theme-text-muted">
            <span className="font-semibold text-theme-text block mb-1">💡 Pro-Tip</span>
            You can change the active <strong className="text-theme-text">Study Area</strong> (e.g. Global vs. India Regional Grid), the <strong className="text-theme-text">Dataset</strong>, or the map <strong className="text-theme-text">Basemap</strong> using the header controls above.
          </div>
        </div>
      )
    }

    // 2. Loading State (Only block layout if we don't have any activeObservation yet)
    if (loading && !activeObservation) {
      return (
        <div className="flex-1 p-6 text-theme-text-sec text-sm flex flex-col items-center justify-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
          <p className="text-theme-text-sec font-medium">Loading soil profile...</p>
        </div>
      )
    }

    // 3. Error State (Only block layout if we don't have any activeObservation yet)
    if (error && !activeObservation) {
      return (
        <div className="flex-1 p-6 text-theme-text-sec text-sm flex flex-col gap-4 overflow-y-auto">
          <div className="bg-red-950/20 border border-red-900/50 p-4 rounded-xl text-xs text-red-600 dark:text-red-400">
            <span className="font-semibold block mb-1">Query Failed:</span>
            {error}
          </div>
        </div>
      )
    }

    // 4. 204 No Content (Water/Ocean/Unmapped) (Only block layout if we aren't loading, or if we have no activeObservation)
    if (!activeObservation && !loading) {
      return (
        <div className="flex-1 p-6 text-theme-text-sec text-sm flex flex-col gap-4 overflow-y-auto">
          <p className="italic text-xs text-theme-text-muted leading-relaxed">
            Water or Unmapped Land. No soil profile is available for this coordinate.
          </p>
        </div>
      )
    }

    // 5. Success State (Render the profile. If loading new point, show subtle indicator)
    const obs = activeObservation || { profiles: [] }
    const profiles = obs.profiles || []
    const activeProfile = profiles[activeProfileIndex] || profiles[0]

    return (
      <div className="flex-1 p-5 text-theme-text-sec text-sm flex flex-col gap-5 overflow-y-auto select-none relative">
        {/* Subtle top progress bar indicating a background reload/update is in progress */}
        {loading && (
          <div className="absolute top-0 left-0 right-0 h-1 bg-theme-btn-bg overflow-hidden z-20">
            <div className="h-full bg-teal-500 animate-pulse w-full duration-1000" style={{ animationDuration: '1.5s' }} />
          </div>
        )}

        {/* Reload Error alert */}
        {error && activeObservation && (
          <div className="bg-red-950/20 border border-red-900/50 p-3 rounded-xl text-xs text-red-650 dark:text-red-400">
            <span className="font-semibold block">Reload Failed:</span> {error}
          </div>
        )}

        {/* Observation Summary Card (Now merged with metadata card fields) */}
        {activeObservation && (
          <ObservationSummary
            observation={activeObservation}
            selectedCoordinate={selectedCoordinate}
            datasetId={activeDatasetId}
          />
        )}

        {/* Profile Selector for multiple profiles */}
        {profiles.length > 0 && (
          <ProfileSelector
            profiles={profiles}
            activeIndex={activeProfileIndex}
            onChange={(idx) => {
              setActiveProfileIndex(idx)
              setActiveLayerIndex(null) // Reset active layer selection on profile switch
            }}
          />
        )}

        {activeProfile ? (
          <div className="flex flex-col gap-6">
            {/* Classification & Context Card */}
            <ClassificationCard profile={activeProfile} />

            {/* Layer List Card (Now embeds properties table inline for the active horizon) */}
            <LayerList
              layers={activeProfile.layers || []}
              activeLayerIndex={activeLayerIndex}
              onLayerSelect={(idx: number | null) => {
                setActiveLayerIndex(idx)
              }}
            />
          </div>
        ) : (
          !loading && <div className="text-xs text-theme-text-muted italic">No profile data available.</div>
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen w-screen bg-theme-bg text-theme-text overflow-hidden font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 bg-theme-panel backdrop-blur-md border-b border-theme-border z-10 shadow-sm select-none">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-bold bg-gradient-to-r from-teal-500 via-cyan-500 to-sky-500 dark:from-teal-400 dark:via-cyan-400 dark:to-sky-400 bg-clip-text text-transparent tracking-tight">
            Global Soil Explorer
          </h1>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-theme-btn-bg text-theme-btn-text border border-theme-btn-border font-mono font-medium">
            V1.0
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* Study Area Dropdown */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-theme-text-muted font-medium">Study Area:</span>
            <select
              value={activeStudyArea.id}
              onChange={handleStudyAreaChange}
              className="w-44 bg-theme-btn-bg border border-theme-btn-border hover:border-teal-500/30 px-3 py-1.5 rounded-lg text-theme-text text-xs outline-none focus:border-teal-500/60 focus:ring-1 focus:ring-teal-500/30 transition-all cursor-pointer backdrop-blur-sm"
            >
              {studyAreaRegistry.list().map((id) => (
                <option key={id} value={id} className="bg-theme-bg text-theme-text">
                  {studyAreaRegistry.get(id).name}
                </option>
              ))}
            </select>
          </div>

          {/* Dataset Dropdown */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-theme-text-muted font-medium">Dataset:</span>
            <select
              value={activeDatasetId}
              onChange={handleDatasetChange}
              className="w-28 bg-theme-btn-bg border border-theme-btn-border hover:border-teal-500/30 px-3 py-1.5 rounded-lg text-theme-text text-xs outline-none focus:border-teal-500/60 focus:ring-1 focus:ring-teal-500/30 transition-all cursor-pointer backdrop-blur-sm"
            >
              {activeStudyArea.availableDatasets.map((ds) => (
                <option key={ds} value={ds} className="bg-theme-bg text-theme-text">
                  {ds.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {/* Basemap Dropdown */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-theme-text-muted font-medium">Basemap:</span>
            <select
              value={basemap}
              onChange={handleBasemapChange}
              className="w-28 bg-theme-btn-bg border border-theme-btn-border hover:border-teal-500/30 px-3 py-1.5 rounded-lg text-theme-text text-xs outline-none focus:border-teal-500/60 focus:ring-1 focus:ring-teal-500/30 transition-all cursor-pointer backdrop-blur-sm"
            >
              {activeStudyArea.availableBasemaps.map((bm) => (
                <option key={bm} value={bm} className="bg-theme-bg text-theme-text">
                  {bm.charAt(0).toUpperCase() + bm.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* Main Workspace layout */}
      <div className="flex flex-1 relative overflow-hidden">
        {/* Sidebar */}
        <aside
          className={`flex flex-col border-r border-theme-border bg-theme-panel backdrop-blur-md z-10 transition-all duration-300 ${
            sidebarOpen ? 'w-80' : 'w-0 overflow-hidden border-none'
          }`}
        >
          <div className="p-4 border-b border-theme-border flex items-center relative select-none bg-theme-btn-bg/10 h-14">
            {/* Centered Title */}
            <h2 className="absolute inset-0 flex items-center justify-center font-bold text-theme-text tracking-wider text-[11px] uppercase pointer-events-none">
              Layer Manager
            </h2>
            {/* Collapse hamburger button on the right */}
            <button
              onClick={toggleSidebar}
              className="ml-auto p-1.5 rounded-lg hover:bg-theme-btn-bg/85 text-theme-text-muted hover:text-theme-text transition-all cursor-pointer z-10"
              title="Collapse Sidebar"
            >
              <Menu className="w-4 h-4" />
            </button>
          </div>
          <div className="flex-1 p-6 text-theme-text-sec text-sm flex flex-col gap-4 overflow-y-auto">
            <LayerLegendPanel />
            <BookmarksPanel />
          </div>
        </aside>

        <main className="flex-1 h-full w-full relative bg-theme-bg-sec">
          {/* Floating toggle layer sidebar button */}
          {!sidebarOpen && (
            <button
              onClick={toggleSidebar}
              className="absolute top-4 left-4 z-20 px-3.5 py-2 rounded-xl bg-theme-panel border border-theme-border text-xs font-semibold text-theme-text-sec hover:text-teal-650 dark:hover:text-teal-400 shadow-md hover:border-teal-500/35 transition-all cursor-pointer flex items-center gap-2 h-10"
              title="Open Layer Manager"
            >
              <Layers className="w-4 h-4 text-teal-500" />
              <span>Layers</span>
            </button>
          )}

          <div
            id="map-canvas-container"
            ref={mapContainerRef}
            className="h-full w-full absolute inset-0"
          />

          {/* Search bar */}
          <SearchBox />

          {/* Map zoom and home navigation controls */}
          <NavigationControls />

          {/* Floating toggle scientific panel button */}
          {!infoPanelOpen && (
            <button
              onClick={() => setInfoPanelOpen(true)}
              className="absolute top-4 right-4 z-20 px-3.5 py-2 rounded-xl bg-theme-panel border border-theme-border text-xs font-semibold text-theme-text-sec hover:text-teal-650 dark:hover:text-teal-400 shadow-md hover:border-teal-500/35 transition-all cursor-pointer flex items-center gap-2 h-10"
              title="Show Scientific Info"
            >
              <Info className="w-4 h-4 text-teal-500" />
              <span>Profile</span>
            </button>
          )}
        </main>

        {/* Information Panel */}
        <aside
          className={`flex flex-col border-l border-theme-border bg-theme-panel backdrop-blur-md z-10 transition-all duration-300 ${
            infoPanelOpen ? 'w-96' : 'w-0 overflow-hidden border-none'
          }`}
        >
          <div className="p-4 border-b border-theme-border flex items-center relative select-none bg-theme-btn-bg/10 h-14">
            {/* Collapse hamburger button on the left */}
            <button
              onClick={() => setInfoPanelOpen(false)}
              className="p-1.5 rounded-lg hover:bg-theme-btn-bg/85 text-theme-text-muted hover:text-theme-text transition-all cursor-pointer z-10"
              title="Collapse Scientific Profile"
            >
              <Menu className="w-4 h-4" />
            </button>
            {/* Centered Title */}
            <h2 className="absolute inset-0 flex items-center justify-center font-bold text-theme-text tracking-wider text-[11px] uppercase pointer-events-none">
              Scientific Profile
            </h2>
          </div>
          {renderScientificProfile()}
        </aside>
      </div>

      {/* Status Bar */}
      <footer className="flex items-center justify-between px-6 py-2.5 bg-theme-bg-sec border-t border-theme-border text-xs text-theme-text-muted select-none z-10 font-mono">
        <div className="flex items-center gap-4">
          <span>Map Engine: {isInitialized ? 'ONLINE' : 'BOOTING'}</span>
          <span>Center: {center[0].toFixed(4)}°E, {center[1].toFixed(4)}°N</span>
          {hoverCoord && (
            <span>Cursor: {hoverCoord.longitude.toFixed(4)}°E, {hoverCoord.latitude.toFixed(4)}°N</span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 mr-4 border-r border-theme-border pr-4">
            <button
              onClick={() => {
                try {
                  commandManager.undo()
                } catch (e) {
                  logger.error('Undo error:', e)
                }
              }}
              className="p-1 rounded-lg bg-theme-btn-bg hover:bg-theme-btn-bg/85 border border-theme-btn-border text-theme-text hover:text-teal-650 dark:hover:text-teal-400 transition-colors cursor-pointer flex items-center justify-center"
              title="Undo last selection"
            >
              <Undo className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => {
                try {
                  commandManager.redo()
                } catch (e) {
                  logger.error('Redo error:', e)
                }
              }}
              className="p-1 rounded-lg bg-theme-btn-bg hover:bg-theme-btn-bg/85 border border-theme-btn-border text-theme-text hover:text-teal-650 dark:hover:text-teal-400 transition-colors cursor-pointer flex items-center justify-center"
              title="Redo last selection"
            >
              <Redo className="w-3.5 h-3.5" />
            </button>
          </div>
          <span>Projection: {activeStudyArea.projection}</span>
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-600 dark:bg-emerald-500 animate-pulse shadow-[0_0_8px_#10b981]" />
            API Connected
          </span>
        </div>
      </footer>
    </div>
  )
}
