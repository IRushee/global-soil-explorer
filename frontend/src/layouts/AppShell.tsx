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
  ClassificationCard,
  MetadataCard
} from '../components/ScientificPanelComponents'
import { SearchBox, NavigationControls, BookmarksPanel } from '../components/SearchAndNavigation'

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
        <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4 overflow-y-auto">
          <p className="italic text-xs text-slate-500">
            No active coordinate selected. Click the map to resolve coordinates.
          </p>
        </div>
      )
    }

    // 2. Loading State
    if (loading) {
      return (
        <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col items-center justify-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-500"></div>
          <p className="text-slate-400 font-medium">Loading soil profile...</p>
        </div>
      )
    }

    // 3. Error State
    if (error) {
      return (
        <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4 overflow-y-auto">
          <div className="bg-red-950/40 border border-red-900/50 p-4 rounded-lg text-xs text-red-400">
            <span className="font-semibold block mb-1">Query Failed:</span>
            {error}
          </div>
        </div>
      )
    }

    // 4. 204 No Content (Water/Ocean/Unmapped)
    if (!activeObservation) {
      return (
        <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4 overflow-y-auto">
          <p className="italic text-xs text-slate-500 leading-relaxed">
            Water or Unmapped Land. No soil profile is available for this coordinate.
          </p>
        </div>
      )
    }

    // 5. Success State
    const profiles = activeObservation.profiles || []
    const activeProfile = profiles[activeProfileIndex] || profiles[0]

    return (
      <div className="flex-1 p-5 text-slate-400 text-sm flex flex-col gap-5 overflow-y-auto select-none">
        {/* Observation Summary Card */}
        <ObservationSummary
          observation={activeObservation}
          selectedCoordinate={selectedCoordinate}
          datasetId={activeDatasetId}
        />

        {/* Profile Selector for multiple profiles */}
        <ProfileSelector
          profiles={profiles}
          activeIndex={activeProfileIndex}
          onChange={(idx) => {
            setActiveProfileIndex(idx)
            setActiveLayerIndex(null) // Reset active layer selection on profile switch
          }}
        />

        {activeProfile ? (
          <div className="flex flex-col gap-5">
            {/* Classification & Context Card */}
            <ClassificationCard profile={activeProfile} />

            {/* Layer List Card */}
            <LayerList
              layers={activeProfile.layers || []}
              activeLayerIndex={activeLayerIndex}
              onLayerSelect={(idx) => {
                setActiveLayerIndex(idx)
              }}
            />

            {/* Scientific Properties Table (Only visible when a layer is active) */}
            {activeLayerIndex !== null && activeProfile.layers?.[activeLayerIndex] ? (
              <ScientificPropertyTable layer={activeProfile.layers[activeLayerIndex]} />
            ) : (
              <div className="text-center text-xs text-slate-500 italic border border-dashed border-slate-800 p-4 rounded-lg">
                Click a layer card above to view detailed scientific measurements.
              </div>
            )}
          </div>
        ) : (
          <div className="text-xs text-slate-550 italic">No profile data available.</div>
        )}

        {/* Metadata Card */}
        {activeObservation.metadata && (
          <MetadataCard metadata={activeObservation.metadata} />
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-900 text-slate-100 overflow-hidden font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-slate-850 border-b border-slate-800 z-10 shadow-md">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold bg-gradient-to-r from-teal-400 to-cyan-500 bg-clip-text text-transparent">
            Global Soil Explorer
          </span>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono">
            V1.0
          </span>
        </div>

        <div className="flex items-center gap-4">
          {/* Study Area Dropdown */}
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Study Area:</span>
            <select
              value={activeStudyArea.id}
              onChange={handleStudyAreaChange}
              className="bg-slate-800 border border-slate-700 px-3 py-1 rounded text-slate-200 outline-none focus:border-teal-500 transition-colors"
            >
              {studyAreaRegistry.list().map((id) => (
                <option key={id} value={id}>
                  {studyAreaRegistry.get(id).name}
                </option>
              ))}
            </select>
          </div>

          {/* Dataset Dropdown */}
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Dataset:</span>
            <select
              value={activeDatasetId}
              onChange={handleDatasetChange}
              className="bg-slate-800 border border-slate-700 px-3 py-1 rounded text-slate-200 outline-none focus:border-teal-500 transition-colors"
            >
              {activeStudyArea.availableDatasets.map((ds) => (
                <option key={ds} value={ds}>
                  {ds.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {/* Basemap Dropdown */}
          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-400">Basemap:</span>
            <select
              value={basemap}
              onChange={handleBasemapChange}
              className="bg-slate-800 border border-slate-700 px-3 py-1 rounded text-slate-200 outline-none focus:border-teal-500 transition-colors"
            >
              {activeStudyArea.availableBasemaps.map((bm) => (
                <option key={bm} value={bm}>
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
          className={`flex flex-col border-r border-slate-800 bg-slate-850 z-10 transition-all duration-300 ${
            sidebarOpen ? 'w-80' : 'w-0 overflow-hidden border-none'
          }`}
        >
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <span className="font-semibold text-slate-200">Layer Manager</span>
            <button
              onClick={toggleSidebar}
              className="text-xs px-2 py-1 rounded bg-slate-750 hover:bg-slate-700 transition-colors text-slate-400"
            >
              Collapse
            </button>
          </div>
          <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4 overflow-y-auto">
            <p>Layer controls placeholder. No thematic overlays active.</p>
            <div className="border border-slate-800 bg-slate-900/50 p-4 rounded text-xs leading-relaxed mb-2">
              <span className="text-slate-200 block mb-1 font-semibold">Active Capabilities:</span>
              <ul className="list-disc pl-4 space-y-1 text-slate-400">
                <li>Profiles: {activeStudyArea.capabilities.supportsProfiles ? 'YES' : 'NO'}</li>
                <li>Hydrology: {activeStudyArea.capabilities.supportsHydrology ? 'YES' : 'NO'}</li>
                <li>Offline: {activeStudyArea.capabilities.supportsOffline ? 'YES' : 'NO'}</li>
              </ul>
            </div>
            <BookmarksPanel />
          </div>
        </aside>

        <main className="flex-1 h-full w-full relative bg-slate-950">
          {!sidebarOpen && (
            <button
              onClick={toggleSidebar}
              className="absolute top-4 left-4 z-20 px-3 py-1.5 rounded bg-slate-800/90 hover:bg-slate-750 border border-slate-700 text-xs font-semibold text-slate-200 shadow-lg cursor-pointer"
            >
              Open Layers
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

          {/* Info toggle trigger simulator */}
          <button
            onClick={() => setInfoPanelOpen(!infoPanelOpen)}
            className="absolute top-4 right-4 z-20 px-3 py-1.5 rounded bg-slate-800/90 hover:bg-slate-750 border border-slate-700 text-xs font-semibold text-slate-200 shadow-lg cursor-pointer"
          >
            {infoPanelOpen ? 'Hide Scientific Info' : 'Show Scientific Info'}
          </button>
        </main>

        {/* Information Panel */}
        <aside
          className={`flex flex-col border-l border-slate-800 bg-slate-850 z-10 transition-all duration-300 ${
            infoPanelOpen ? 'w-96' : 'w-0 overflow-hidden border-none'
          }`}
        >
          <div className="p-4 border-b border-slate-800 flex justify-between items-center select-none">
            <span className="font-semibold text-slate-200">Scientific Profile</span>
            <button
              onClick={() => setInfoPanelOpen(false)}
              className="text-xs px-2 py-1 rounded bg-slate-750 hover:bg-slate-700 transition-colors text-slate-400"
            >
              Close
            </button>
          </div>
          {renderScientificProfile()}
        </aside>
      </div>

      {/* Status Bar */}
      <footer className="flex items-center justify-between px-6 py-2 bg-slate-900 border-t border-slate-800 text-xs text-slate-450 select-none z-10 font-mono">
        <div className="flex items-center gap-4">
          <span>Map Engine: {isInitialized ? 'ONLINE' : 'BOOTING'}</span>
          <span>Center: {center[0].toFixed(4)}°E, {center[1].toFixed(4)}°N</span>
          {hoverCoord && (
            <span>Cursor: {hoverCoord.longitude.toFixed(4)}°E, {hoverCoord.latitude.toFixed(4)}°N</span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 mr-4 border-r border-slate-800 pr-4">
            <button
              onClick={() => {
                try {
                  commandManager.undo()
                } catch (e) {
                  logger.error('Undo error:', e)
                }
              }}
              className="px-2 py-0.5 rounded bg-slate-850 hover:bg-slate-800 border border-slate-750 text-slate-350 transition-colors cursor-pointer"
              title="Undo last selection"
            >
              Undo
            </button>
            <button
              onClick={() => {
                try {
                  commandManager.redo()
                } catch (e) {
                  logger.error('Redo error:', e)
                }
              }}
              className="px-2 py-0.5 rounded bg-slate-850 hover:bg-slate-800 border border-slate-750 text-slate-350 transition-colors cursor-pointer"
              title="Redo last selection"
            >
              Redo
            </button>
          </div>
          <span>Projection: {activeStudyArea.projection}</span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            API Connected
          </span>
        </div>
      </footer>
    </div>
  )
}
