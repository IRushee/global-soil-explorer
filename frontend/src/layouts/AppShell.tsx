import React, { useEffect, useRef } from 'react'
import { useGlobalStore } from '../store'
import { mapRenderer } from '../map/wrapper'
import { studyAreaRegistry } from '../services/studyArea'
import { logger } from '../utils/logger'

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
  } = useGlobalStore()

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
          <div className="p-4 border-b border-slate-800 flex justify-between items-center">
            <span className="font-semibold text-slate-200">Scientific Profile</span>
            <button
              onClick={() => setInfoPanelOpen(false)}
              className="text-xs px-2 py-1 rounded bg-slate-750 hover:bg-slate-700 transition-colors text-slate-400"
            >
              Close
            </button>
          </div>
          <div className="flex-1 p-6 text-slate-400 text-sm flex flex-col gap-4">
            <p>Scientific information panel container placeholder.</p>
            <p className="italic text-xs text-slate-500">
              No active coordinate selected. Click the map to resolve coordinates.
            </p>
          </div>
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
