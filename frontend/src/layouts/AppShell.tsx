import React, { useEffect, useRef, useState } from 'react'
import { useGlobalStore } from '../store'
import { mapRenderer } from '../map/wrapper'
import { studyAreaRegistry } from '../services/studyArea'
import { logger } from '../utils/logger'
import { soilApi } from '../api/client'

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
  } = useGlobalStore()

  // Local state for loading, error, and profile tabs
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeProfileIndex, setActiveProfileIndex] = useState(0)

  // Ref to hold the map click handler to avoid stale closures
  const clickHandlerRef = useRef<((e: any) => void) | null>(null)

  // Keep clickHandlerRef updated with latest logic
  useEffect(() => {
    clickHandlerRef.current = async (e: any) => {
      const coord = e.coordinate
      setSelectedCoordinate(coord)
      setInfoPanelOpen(true)
      setLoading(true)
      setError(null)
      try {
        const obs = await soilApi.getSoilObservation(coord)
        setActiveObservation(obs)
        setActiveProfileIndex(0) // Reset tab index on successful fetch
      } catch (err: any) {
        logger.error('Failed to retrieve soil observation:', err)
        setError(err.message || 'Failed to retrieve soil observation')
        setActiveObservation(null)
      } finally {
        setLoading(false)
      }
    }
  })

  // Initialize Map wrapper on shell mount
  useEffect(() => {
    if (mapContainerRef.current) {
      try {
        mapRenderer.initialize('map-canvas-container', {
          container: 'map-canvas-container',
          style: {
            version: 8,
            sources: {
              'osm-tiles': {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: '© OpenStreetMap contributors',
              },
            },
            layers: [
              {
                id: 'osm-layer',
                type: 'raster',
                source: 'osm-tiles',
                minzoom: 0,
                maxzoom: 19,
              },
            ],
          },
          center: center,
          zoom: zoom,
        })
        setInitialized(true)
        logger.info('Map wrapper initialized inside AppShell layout')

        // Register the map click event handler exactly once, forwarding to the ref
        mapRenderer.on('click', (e) => {
          if (clickHandlerRef.current) {
            clickHandlerRef.current(e)
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

  const handleStudyAreaChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const areaId = e.target.value
    const area = studyAreaRegistry.get(areaId)
    setActiveStudyArea(area)
    mapRenderer.setCenter(
      (area.bounds[0][1] + area.bounds[1][1]) / 2,
      (area.bounds[0][0] + area.bounds[1][0]) / 2
    )
    mapRenderer.setZoom(area.defaultZoom)
  }

  // Helper to extract properties from layers (measurements or fallback to properties array)
  const getPropertyValue = (layer: any, type: 'ph' | 'organic_carbon' | 'sand' | 'silt' | 'clay'): number | null => {
    if (layer.measurements) {
      if (type === 'ph' && layer.measurements.chemical?.ph !== undefined && layer.measurements.chemical?.ph !== null) return layer.measurements.chemical.ph
      if (type === 'organic_carbon' && layer.measurements.chemical?.organic_carbon !== undefined && layer.measurements.chemical?.organic_carbon !== null) return layer.measurements.chemical.organic_carbon
      if (type === 'sand' && layer.measurements.physical?.sand !== undefined && layer.measurements.physical?.sand !== null) return layer.measurements.physical.sand
      if (type === 'silt' && layer.measurements.physical?.silt !== undefined && layer.measurements.physical?.silt !== null) return layer.measurements.physical.silt
      if (type === 'clay' && layer.measurements.physical?.clay !== undefined && layer.measurements.physical?.clay !== null) return layer.measurements.physical.clay
    }
    
    if (layer.properties && Array.isArray(layer.properties)) {
      const map: Record<string, string[]> = {
        ph: ['ph_water', 'ph'],
        organic_carbon: ['organic_carbon', 'organic carbon'],
        sand: ['sand'],
        silt: ['silt'],
        clay: ['clay'],
      }
      const searchTypes = map[type] || [type]
      const prop = layer.properties.find((p: any) =>
        searchTypes.includes(p.property_type.toLowerCase())
      )
      return prop && prop.value !== undefined ? prop.value : null
    }
    
    return null
  }

  // Helper to resolve pH acidity category and style attributes
  const getPhAcidityInfo = (ph: number) => {
    if (ph < 4.5) {
      return {
        category: 'Extremely Acidic',
        bgClass: 'bg-red-950/50 text-red-400 border-red-900/50',
        textClass: 'text-red-400',
      }
    }
    if (ph < 5.1) {
      return {
        category: 'Very Strongly Acidic',
        bgClass: 'bg-orange-950/50 text-orange-400 border-orange-900/50',
        textClass: 'text-orange-400',
      }
    }
    if (ph < 5.6) {
      return {
        category: 'Strongly Acidic',
        bgClass: 'bg-amber-950/50 text-amber-400 border-amber-900/50',
        textClass: 'text-amber-400',
      }
    }
    if (ph < 6.1) {
      return {
        category: 'Moderately Acidic',
        bgClass: 'bg-yellow-950/50 text-yellow-450 border-yellow-900/50',
        textClass: 'text-yellow-450',
      }
    }
    if (ph < 6.6) {
      return {
        category: 'Slightly Acidic',
        bgClass: 'bg-lime-950/50 text-lime-400 border-lime-900/50',
        textClass: 'text-lime-400',
      }
    }
    if (ph < 7.4) {
      return {
        category: 'Neutral',
        bgClass: 'bg-emerald-950/50 text-emerald-400 border-emerald-900/50',
        textClass: 'text-emerald-400',
      }
    }
    if (ph < 7.9) {
      return {
        category: 'Slightly Alkaline',
        bgClass: 'bg-teal-950/50 text-teal-400 border-teal-900/50',
        textClass: 'text-teal-400',
      }
    }
    if (ph < 8.5) {
      return {
        category: 'Moderately Alkaline',
        bgClass: 'bg-cyan-950/50 text-cyan-400 border-cyan-900/50',
        textClass: 'text-cyan-400',
      }
    }
    if (ph <= 9.0) {
      return {
        category: 'Strongly Alkaline',
        bgClass: 'bg-blue-950/50 text-blue-400 border-blue-900/50',
        textClass: 'text-blue-400',
      }
    }
    return {
      category: 'Very Strongly Alkaline',
      bgClass: 'bg-purple-950/50 text-purple-400 border-purple-900/50',
      textClass: 'text-purple-400',
    }
  }

  // Render method for the Scientific Profile Panel based on state
  const renderScientificProfile = () => {
    // 1. Initial State
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
          <p className="text-slate-400">Loading soil profile...</p>
        </div>
      )
    }

    // 3. Error State
    if (error) {
      return (
        <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4 overflow-y-auto">
          <div className="bg-red-950/50 border border-red-900/50 p-4 rounded text-xs text-red-400">
            <span className="font-semibold block mb-1">Query Failed:</span>
            {error}
          </div>
        </div>
      )
    }

    // 4. 204 No Content (Water/Ocean)
    if (!activeObservation) {
      return (
        <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4 overflow-y-auto">
          <p className="italic text-xs text-slate-500">
            Water or Unmapped Land. No soil profile is available for this coordinate.
          </p>
        </div>
      )
    }

    // 5. Success State
    const activeProfile = activeObservation.profiles?.[activeProfileIndex] || activeObservation.profiles?.[0]
    
    return (
      <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4 overflow-y-auto">
        {/* Coordinate Metadata */}
        <div className="border border-slate-800 bg-slate-900/50 p-3 rounded text-xs">
          <span className="text-slate-200 block mb-1 font-semibold">Location Metadata:</span>
          <div className="grid grid-cols-2 gap-2 text-slate-400 font-mono">
            <div>Lat: {selectedCoordinate.latitude.toFixed(6)}°</div>
            <div>Lon: {selectedCoordinate.longitude.toFixed(6)}°</div>
          </div>
        </div>

        {/* Tabbed Control for Multiple Profiles */}
        {activeObservation.profiles && activeObservation.profiles.length > 1 && (
          <div className="flex flex-col gap-2 mb-2">
            <span className="text-xs font-semibold text-slate-400">Mapping Unit Components:</span>
            <div className="flex flex-wrap gap-1.5 border-b border-slate-800 pb-2">
              {activeObservation.profiles.map((profile, idx) => {
                const shareVal = profile.composition_share !== null && profile.composition_share !== undefined
                  ? (profile.composition_share <= 1 ? Math.round(profile.composition_share * 100) : Math.round(profile.composition_share))
                  : null
                const shareStr = shareVal !== null ? ` (${shareVal}%)` : ''
                const name = profile.classification.class_name
                const isActive = idx === activeProfileIndex
                return (
                  <button
                    key={idx}
                    onClick={() => setActiveProfileIndex(idx)}
                    className={`text-xs px-2.5 py-1.5 rounded transition-all font-medium border ${
                      isActive
                        ? 'bg-teal-900/30 text-teal-350 border-teal-800/80 shadow'
                        : 'bg-slate-800/50 text-slate-400 border-transparent hover:bg-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {name}{shareStr}
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* Active Profile Info */}
        {activeProfile ? (
          <div className="flex flex-col gap-4">
            {/* Classification Header (if single profile) */}
            {activeObservation.profiles.length === 1 && (
              <div className="border-b border-slate-800 pb-2">
                <span className="text-xs text-slate-500 uppercase font-semibold">Classification</span>
                <div className="text-slate-200 font-semibold">{activeProfile.classification.class_name}</div>
              </div>
            )}

            {/* Depth Layers Stack */}
            <div className="flex flex-col gap-3">
              <span className="text-xs font-semibold text-slate-400">Soil Layers:</span>
              {activeProfile.layers && activeProfile.layers.length > 0 ? (
                activeProfile.layers.map((layer, index) => {
                  const ph = getPropertyValue(layer, 'ph')
                  const oc = getPropertyValue(layer, 'organic_carbon')
                  const sand = getPropertyValue(layer, 'sand')
                  const silt = getPropertyValue(layer, 'silt')
                  const clay = getPropertyValue(layer, 'clay')

                  const phInfo = ph !== null ? getPhAcidityInfo(ph) : null

                  return (
                    <div key={index} className="border border-slate-800 bg-slate-900/30 rounded-lg p-4 flex flex-col gap-3 shadow-sm">
                      {/* Depth range & acidity category badge */}
                      <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                        <span className="font-semibold text-slate-200 text-sm">
                          {layer.top_depth_cm} - {layer.bottom_depth_cm} cm
                        </span>
                        {phInfo && (
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium border ${phInfo.bgClass}`}>
                            {phInfo.category}
                          </span>
                        )}
                      </div>

                      {/* Chemical Properties grid */}
                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="flex flex-col gap-1">
                          <span className="text-slate-400 font-medium">pH (Water):</span>
                          <span className={`font-mono font-semibold ${phInfo ? phInfo.textClass : 'text-slate-400'}`}>
                            {ph !== null ? ph.toFixed(2) : 'N/A'}
                          </span>
                        </div>
                        <div className="flex flex-col gap-1">
                          <span className="text-slate-400 font-medium">Organic Carbon:</span>
                          <span className="text-slate-200 font-mono font-semibold">
                            {oc !== null ? `${oc.toFixed(2)}%` : 'N/A'}
                          </span>
                        </div>
                      </div>

                      {/* Physical texture percentages progress bar */}
                      <div className="flex flex-col gap-1.5 mt-1">
                        <span className="text-slate-400 font-medium text-xs">Soil Texture Components:</span>
                        {sand !== null || silt !== null || clay !== null ? (
                          <div>
                            <div className="flex w-full h-3 rounded-full overflow-hidden bg-slate-800/80 border border-slate-700">
                              {sand !== null && (
                                <div
                                  style={{ width: `${sand}%` }}
                                  className="bg-amber-500 h-full transition-all duration-300"
                                  title={`Sand: ${sand}%`}
                                />
                              )}
                              {silt !== null && (
                                <div
                                  style={{ width: `${silt}%` }}
                                  className="bg-slate-400 h-full transition-all duration-300"
                                  title={`Silt: ${silt}%`}
                                />
                              )}
                              {clay !== null && (
                                <div
                                  style={{ width: `${clay}%` }}
                                  className="bg-red-500 h-full transition-all duration-300"
                                  title={`Clay: ${clay}%`}
                                />
                              )}
                            </div>
                            <div className="flex justify-between text-[10px] font-mono mt-1.5 text-slate-450">
                              <span className="flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-amber-500 inline-block"></span>
                                Sand: {sand !== null ? `${sand.toFixed(1)}%` : 'N/A'}
                              </span>
                              <span className="flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-slate-400 inline-block"></span>
                                Silt: {silt !== null ? `${silt.toFixed(1)}%` : 'N/A'}
                              </span>
                              <span className="flex items-center gap-1">
                                <span className="w-2 h-2 rounded-full bg-red-500 inline-block"></span>
                                Clay: {clay !== null ? `${clay.toFixed(1)}%` : 'N/A'}
                              </span>
                            </div>
                          </div>
                        ) : (
                          <span className="text-slate-500 italic text-[11px]">No texture component data available.</span>
                        )}
                      </div>
                    </div>
                  )
                })
              ) : (
                <div className="text-xs text-slate-500 italic">No depth layers available.</div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-550 italic">No profile data available.</div>
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
              onChange={(e) => setActiveDatasetId(e.target.value)}
              className="bg-slate-800 border border-slate-700 px-3 py-1 rounded text-slate-200 outline-none focus:border-teal-500 transition-colors"
            >
              {activeStudyArea.availableDatasets.map((ds) => (
                <option key={ds} value={ds}>
                  {ds.toUpperCase()}
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
          <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4">
            <p>Layer controls placeholder. No thematic overlays active.</p>
            <div className="border border-slate-800 bg-slate-900/50 p-4 rounded text-xs leading-relaxed">
              <span className="text-slate-200 block mb-1 font-semibold">Active Capabilities:</span>
              <ul className="list-disc pl-4 space-y-1 text-slate-400">
                <li>Profiles: {activeStudyArea.capabilities.supportsProfiles ? 'YES' : 'NO'}</li>
                <li>Hydrology: {activeStudyArea.capabilities.supportsHydrology ? 'YES' : 'NO'}</li>
                <li>Offline: {activeStudyArea.capabilities.supportsOffline ? 'YES' : 'NO'}</li>
              </ul>
            </div>
          </div>
        </aside>

        {/* Map Container */}
        <main className="flex-1 h-full w-full relative bg-slate-950">
          {!sidebarOpen && (
            <button
              onClick={toggleSidebar}
              className="absolute top-4 left-4 z-20 px-3 py-1.5 rounded bg-slate-800/90 hover:bg-slate-750 border border-slate-700 text-xs font-semibold text-slate-200 shadow-lg"
            >
              Open Layers
            </button>
          )}

          <div
            id="map-canvas-container"
            ref={mapContainerRef}
            className="h-full w-full absolute inset-0"
          />

          {/* Info toggle trigger simulator */}
          <button
            onClick={() => setInfoPanelOpen(!infoPanelOpen)}
            className="absolute top-4 right-4 z-20 px-3 py-1.5 rounded bg-slate-800/90 hover:bg-slate-750 border border-slate-700 text-xs font-semibold text-slate-200 shadow-lg"
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
        </div>
        <div className="flex items-center gap-4">
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
