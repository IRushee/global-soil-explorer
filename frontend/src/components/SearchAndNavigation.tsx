import React, { useState, useEffect, useRef } from 'react'
import { Search, X, MapPin, Bookmark as BookmarkIcon, History, Plus, Minus, Home, Trash2, Edit } from 'lucide-react'
import { useGlobalStore, Bookmark } from '../store'
import { mapRenderer } from '../map/wrapper'
import { soilApi } from '../api/client'
import { eventBus } from '../utils/eventBus'
import { logger } from '../utils/logger'
import { Coordinate, SearchProvider, SearchResultItem } from '../types'

// 1. OpenStreetMap Nominatim Search Provider Implementation
export class NominatimSearchProvider implements SearchProvider {
  id = 'nominatim'
  name = 'OpenStreetMap Nominatim'

  async search(query: string, bounds?: [[number, number], [number, number]]): Promise<SearchResultItem[]> {
    if (!query || query.trim().length < 2) return []
    try {
      let url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=6&addressdetails=1`
      if (bounds) {
        // bounds: [[west, south], [east, north]]
        const [[west, south], [east, north]] = bounds
        url += `&viewbox=${west},${north},${east},${south}&bounded=1`
      }

      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'Global-Soil-Explorer-WebGIS'
        }
      })
      if (!response.ok) {
        throw new Error(`Nominatim response error: ${response.statusText}`)
      }
      const data = await response.json()
      if (!Array.isArray(data)) return []

      return data.map((item: any, idx: number) => {
        const address = item.address || {}
        // Resolve a short, clean label
        const city = address.city || address.town || address.village || address.suburb || ''
        const state = address.state || ''
        const country = address.country || ''
        const parts = [item.name || city, state, country].filter(p => p !== '')
        const label = parts.length > 0 ? parts.join(', ') : item.display_name

        return {
          id: `nominatim-${item.place_id || idx}`,
          label,
          category: 'location',
          coordinate: {
            lat: parseFloat(item.lat),
            lon: parseFloat(item.lon),
          },
          score: 1.0 - idx * 0.1,
        }
      })
    } catch (e) {
      logger.error('Nominatim search failed:', e)
      return []
    }
  }
}

// Coordinate Parser Helper
export const parseCoordinates = (query: string): Coordinate | null => {
  const clean = query.trim().replace(/[°'"“”]/g, '') // remove degree/quote symbols
  // Match decimal numbers optionally followed by N/S/E/W direction suffixes
  const numRegex = /([+-]?\d+(?:\.\d+)?)\s*([NSnsEWew]?)/g
  const matches = [...clean.matchAll(numRegex)]
  
  if (matches.length === 2) {
    let latVal = parseFloat(matches[0][1])
    const latDir = matches[0][2].toUpperCase()
    let lonVal = parseFloat(matches[1][1])
    const lonDir = matches[1][2].toUpperCase()
    
    // Apply sign depending on compass direction suffix
    if (latDir === 'S') latVal = -Math.abs(latVal)
    if (latDir === 'N') latVal = Math.abs(latVal)
    if (lonDir === 'W') lonVal = -Math.abs(lonVal)
    if (lonDir === 'E') lonVal = Math.abs(lonVal)
    
    // Check for prefix compass direction if no suffix was matched
    if (!latDir) {
      const matchPrefix = clean.match(/([NSns])\s*[+-]?\d+(?:\.\d+)?/)
      if (matchPrefix) {
        const prefix = matchPrefix[1].toUpperCase()
        if (prefix === 'S') latVal = -Math.abs(latVal)
      }
    }
    if (!lonDir) {
      const matchPrefix = clean.match(/([EWew])\s*[+-]?\d+(?:\.\d+)?/)
      if (matchPrefix) {
        const prefix = matchPrefix[1].toUpperCase()
        if (prefix === 'W') lonVal = -Math.abs(lonVal)
      }
    }
    
    // Latitude standard is [-90, 90], Longitude standard is [-180, 180].
    // If the input was swapped (longitude first), auto-correct.
    let lat = latVal
    let lon = lonVal
    if ((lat < -90 || lat > 90) && (lon >= -90 && lon <= 90)) {
      lat = lonVal
      lon = latVal
    }
    
    if (lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
      return { latitude: lat, longitude: lon }
    }
  }
  return null
}

// 2. SearchBox Component
export const SearchBox: React.FC = () => {
  const [query, setQuery] = useState('')
  const [suggestions, setSuggestions] = useState<SearchResultItem[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const {
    activeStudyArea,
    bookmarks,
    history,
    addHistory,
    setSelectedCoordinate,
    setActiveObservation,
    setInfoPanelOpen,
    setLoading,
    setError,
    setActiveProfileIndex,
    setActiveLayerIndex,
    sidebarOpen,
    setSidebarOpen,
  } = useGlobalStore()

  const provider = useRef(new NominatimSearchProvider())

  // Handle Search Fetch on Query Change
  useEffect(() => {
    const delayDebounce = setTimeout(async () => {
      if (query.trim().length < 2) {
        setSuggestions([])
        return
      }

      const results: SearchResultItem[] = []

      // A. Check for coordinate input
      const coord = parseCoordinates(query)
      if (coord) {
        results.push({
          id: 'coord-search',
          label: `Go to Coordinate: ${coord.latitude.toFixed(4)}, ${coord.longitude.toFixed(4)}`,
          category: 'coordinate',
          coordinate: { lat: coord.latitude, lon: coord.longitude },
          score: 2.0,
        })
      }

      // B. Search registered Place Geocoder (OSM Nominatim)
      try {
        const placeResults = await provider.current.search(query, activeStudyArea.bounds)
        results.push(...placeResults)
      } catch (e) {
        logger.error('Search box geocoding fetch failure:', e)
      }

      // C. Search local Bookmarks
      const matchedBookmarks = (bookmarks as Bookmark[])
        .filter(b => b.name.toLowerCase().includes(query.toLowerCase()))
        .map(b => ({
          id: b.id,
          label: `Bookmark: ${b.name}`,
          category: 'bookmark' as const,
          coordinate: { lat: b.latitude, lon: b.longitude },
          score: 1.5,
        }))
      results.push(...matchedBookmarks)

      // D. Search local History
      const matchedHistory = (history as any[])
        .filter(h => h.name.toLowerCase().includes(query.toLowerCase()))
        .map(h => ({
          id: h.id,
          label: `History: ${h.name}`,
          category: 'history' as const,
          coordinate: { lat: h.latitude, lon: h.longitude },
          score: 1.2,
        }))
      results.push(...matchedHistory)

      // Deduplicate results by exact coordinates
      const seen = new Set<string>()
      const uniqueResults = results.filter(item => {
        const key = `${item.coordinate.lat.toFixed(5)},${item.coordinate.lon.toFixed(5)}`
        if (seen.has(key)) return false
        seen.add(key)
        return true
      })

      setSuggestions(uniqueResults.slice(0, 8))
    }, 300)

    return () => clearTimeout(delayDebounce)
  }, [query, bookmarks, history, activeStudyArea])

  // Close dropdown on outside click
  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  // Execute fly-to and backend soil retrieval
  const handleSelect = async (item: SearchResultItem) => {
    setQuery('')
    setIsOpen(false)
    setActiveIndex(-1)
    if (inputRef.current) inputRef.current.blur()

    const lat = item.coordinate.lat
    const lon = item.coordinate.lon

    logger.info(`Navigating to query: ${item.label} [${lat}, ${lon}]`)
    
    // Smooth Fly-to Animation
    mapRenderer.flyTo(lat, lon, 9)
    mapRenderer.setSelectionMarker(lat, lon)

    // Store Update & Fetch Pipeline
    const coord = { latitude: lat, longitude: lon }
    setSelectedCoordinate(coord)
    eventBus.dispatch('CoordinateSelected', coord)

    // Update History (Deduplicated inside store)
    addHistory({ latitude: lat, longitude: lon, name: item.label.replace(/^(Bookmark|History|Go to Coordinate): /, '') } as any)

    setInfoPanelOpen(true)
    setSidebarOpen(false)
    setLoading(true)
    setError(null)
    try {
      const obs = await soilApi.getSoilObservation(coord)
      setActiveObservation(obs)
      eventBus.dispatch('ObservationLoaded', obs)
      setActiveProfileIndex(0)
      setActiveLayerIndex(null)
    } catch (err: any) {
      logger.error('Failed to retrieve soil observation after navigation:', err)
      setError(err.message || 'Failed to retrieve soil observation')
      setActiveObservation(null)
      eventBus.dispatch('ObservationLoaded', null)
    } finally {
      setLoading(false)
    }
  }

  // Keyboard navigation handler
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || suggestions.length === 0) return

    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIndex(prev => (prev + 1) % suggestions.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIndex(prev => (prev - 1 + suggestions.length) % suggestions.length)
    } else if (e.key === 'Enter') {
      e.preventDefault()
      if (activeIndex >= 0 && activeIndex < suggestions.length) {
        handleSelect(suggestions[activeIndex])
      } else if (suggestions.length > 0) {
        handleSelect(suggestions[0])
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false)
      setActiveIndex(-1)
    }
  }

  const leftClass = sidebarOpen ? 'left-4' : 'left-16'
  return (
    <div ref={dropdownRef} className={`absolute top-4 ${leftClass} z-20 w-80 font-sans transition-all duration-300`}>
      <div className="relative flex items-center bg-theme-panel border border-theme-border hover:border-teal-500/35 rounded-xl shadow-md transition-all duration-300">
        <Search className="w-4 h-4 ml-3 text-theme-text-muted pointer-events-none" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setIsOpen(true)
            setActiveIndex(-1)
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search coordinates or places..."
          className="w-full bg-transparent border-none outline-none px-3 py-2.5 text-xs text-theme-text placeholder-theme-text-muted"
        />
        {query && (
          <button
            onClick={() => {
              setQuery('')
              setSuggestions([])
            }}
            className="p-1 mr-2 text-theme-text-muted hover:text-theme-text cursor-pointer"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Auto-suggest Dropdown */}
      {isOpen && (query.trim().length >= 2 || suggestions.length > 0) && (
        <div className="absolute top-11 left-0 w-full bg-theme-panel border border-theme-border rounded-xl shadow-lg overflow-hidden z-30 mt-1 animate-fadeIn">
          {suggestions.length > 0 ? (
            <ul className="max-h-60 overflow-y-auto">
              {suggestions.map((item, idx) => {
                const isActive = idx === activeIndex
                return (
                  <li
                    key={item.id}
                    onClick={() => handleSelect(item)}
                    onMouseEnter={() => setActiveIndex(idx)}
                    className={`flex items-center gap-2.5 px-3.5 py-2.5 text-xs transition-colors cursor-pointer border-b border-theme-border-sec last:border-none ${
                      isActive ? 'bg-teal-500/10 text-teal-650 dark:text-teal-400 font-semibold border-l-2 border-teal-500' : 'text-theme-text-sec hover:bg-theme-btn-bg/50 hover:text-theme-text'
                    }`}
                  >
                    {item.category === 'coordinate' && <MapPin className="w-3.5 h-3.5 text-amber-500 shrink-0" />}
                    {item.category === 'bookmark' && <BookmarkIcon className="w-3.5 h-3.5 text-teal-500 shrink-0" />}
                    {item.category === 'history' && <History className="w-3.5 h-3.5 text-theme-text-muted shrink-0" />}
                    {item.category === 'location' && <MapPin className="w-3.5 h-3.5 text-sky-500 shrink-0" />}
                    <span className="truncate">{item.label}</span>
                  </li>
                )
              })}
            </ul>
          ) : (
            <div className="p-3 text-[11px] text-theme-text-muted italic text-center">
              No results found. Type coordinates (e.g. 52.0, 10.0) or place names.
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// 3. NavigationControls (Zoom & Home buttons)
export const NavigationControls: React.FC = () => {
  const {
    activeStudyArea,
    selectedCoordinate,
    setSelectedCoordinate,
    setActiveObservation,
    setInfoPanelOpen,
    sidebarOpen,
  } = useGlobalStore()

  const handleZoomIn = () => {
    const current = mapRenderer.getZoom()
    if (current !== null) {
      mapRenderer.setZoom(Math.min(current + 1, 18))
    }
  }

  const handleZoomOut = () => {
    const current = mapRenderer.getZoom()
    if (current !== null) {
      mapRenderer.setZoom(Math.max(current - 1, 1))
    }
  }

  const handleHome = () => {
    const lat = (activeStudyArea.bounds[0][1] + activeStudyArea.bounds[1][1]) / 2
    const lon = (activeStudyArea.bounds[0][0] + activeStudyArea.bounds[1][0]) / 2
    
    logger.info(`Resetting map view to study area home: [${lon}, ${lat}]`)
    
    // Smooth flying animation home
    mapRenderer.flyTo(lat, lon, activeStudyArea.defaultZoom)

    // Optionally reset selection markers
    mapRenderer.setSelectionMarker(null, null)
    setSelectedCoordinate(null)
    setActiveObservation(null)
    setInfoPanelOpen(false)
  }

  const topOffset = sidebarOpen ? 'top-16' : 'top-28'

  return (
    <div className={`absolute ${topOffset} left-4 z-20 flex flex-col gap-1.5 font-sans transition-all duration-300`}>
      {/* Zoom In */}
      <button
        onClick={handleZoomIn}
        className="p-2.5 rounded-xl bg-theme-panel backdrop-blur-md border border-theme-border hover:border-teal-500/35 text-theme-text hover:text-teal-650 dark:hover:text-teal-400 shadow-md transition-all cursor-pointer flex items-center justify-center h-10 w-10"
        title="Zoom In"
      >
        <Plus className="w-4 h-4" />
      </button>

      {/* Zoom Out */}
      <button
        onClick={handleZoomOut}
        className="p-2.5 rounded-xl bg-theme-panel backdrop-blur-md border border-theme-border hover:border-teal-500/35 text-theme-text hover:text-teal-650 dark:hover:text-teal-400 shadow-md transition-all cursor-pointer flex items-center justify-center h-10 w-10"
        title="Zoom Out"
      >
        <Minus className="w-4 h-4" />
      </button>

      {/* Reset View / Home */}
      <button
        onClick={handleHome}
        className="p-2.5 rounded-xl bg-theme-panel backdrop-blur-md border border-theme-border hover:border-teal-500/35 text-theme-text hover:text-teal-650 dark:hover:text-teal-400 shadow-md transition-all cursor-pointer flex items-center justify-center h-10 w-10"
        title="Reset Map to Home"
      >
        <Home className="w-4 h-4" />
      </button>
    </div>
  )
}

// 4. BookmarksPanel & History Panel Component (For Sidebar placement)
export const BookmarksPanel: React.FC = () => {
  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [newName, setNewName] = useState('')

  const {
    bookmarks,
    history,
    addBookmark,
    removeBookmark,
    renameBookmark,
    clearHistory,
    selectedCoordinate,
    setActiveObservation,
    setSelectedCoordinate,
    setInfoPanelOpen,
    setLoading,
    setError,
    setActiveProfileIndex,
    setActiveLayerIndex,
  } = useGlobalStore()

  // Save current location as a bookmark
  const handleSaveCurrent = () => {
    if (!selectedCoordinate) return
    const lat = selectedCoordinate.latitude
    const lon = selectedCoordinate.longitude
    addBookmark({
      latitude: lat,
      longitude: lon,
    })
  }

  // Load / navigate to a saved coordinate
  const handleNavigate = async (coord: Coordinate, name: string) => {
    const lat = coord.latitude
    const lon = coord.longitude
    mapRenderer.flyTo(lat, lon, 9)
    mapRenderer.setSelectionMarker(lat, lon)

    setSelectedCoordinate(coord)
    eventBus.dispatch('CoordinateSelected', coord)

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
      logger.error('Failed to retrieve soil observation from bookmark:', err)
      setError(err.message || 'Failed to retrieve soil observation')
      setActiveObservation(null)
      eventBus.dispatch('ObservationLoaded', null)
    } finally {
      setLoading(false)
    }
  }

  const startRenaming = (b: Bookmark) => {
    setRenamingId(b.id)
    setNewName(b.name)
  }

  const saveRename = (b: Bookmark) => {
    if (newName.trim()) {
      renameBookmark(b, newName.trim())
    }
    setRenamingId(null)
    setNewName('')
  }

  const isCurrentBookmarked = selectedCoordinate && (bookmarks as Bookmark[]).some(
    b => b.latitude === selectedCoordinate.latitude && b.longitude === selectedCoordinate.longitude
  )

  return (
    <div className="flex flex-col gap-4 font-sans text-xs">
      {/* Bookmarks Section */}
      <div className="border border-theme-border bg-theme-card p-4 rounded-xl flex flex-col gap-3">
        <div className="flex justify-between items-center border-b border-theme-border-sec pb-1.5">
          <span className="font-semibold text-theme-text uppercase tracking-wider text-[10px]">Saved Bookmarks</span>
          {selectedCoordinate && !isCurrentBookmarked && (
            <button
              onClick={handleSaveCurrent}
              className="text-[10px] px-2 py-0.5 rounded bg-teal-500/10 text-teal-650 dark:text-teal-400 hover:bg-teal-500/20 border border-teal-500/30 font-medium transition-colors cursor-pointer"
            >
              Save Current
            </button>
          )}
        </div>

        {(bookmarks as Bookmark[]).length > 0 ? (
          <ul className="flex flex-col gap-1.5 max-h-36 overflow-y-auto pr-1">
            {(bookmarks as Bookmark[]).map((b) => (
              <li
                key={b.id}
                className="flex items-center justify-between gap-2 p-1.5 rounded bg-theme-btn-bg/40 border border-theme-border hover:border-theme-border/80"
              >
                {renamingId === b.id ? (
                  <div className="flex items-center gap-1 w-full">
                    <input
                      type="text"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      className="w-full bg-theme-bg border border-theme-border rounded px-1.5 py-0.5 text-xs text-theme-text outline-none"
                    />
                    <button
                      onClick={() => saveRename(b)}
                      className="px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-655 dark:text-teal-400 hover:bg-teal-500/20 border border-teal-500/30 text-[10px]"
                    >
                      Save
                    </button>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => handleNavigate(b, b.name)}
                      className="text-left font-medium text-theme-text-sec hover:text-theme-text truncate flex-1"
                      title={b.name}
                    >
                      {b.name}
                    </button>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => startRenaming(b)}
                        className="p-1 text-theme-text-muted hover:text-theme-text"
                        title="Rename Bookmark"
                      >
                        <Edit className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => removeBookmark(b)}
                        className="p-1 text-theme-text-muted hover:text-red-500"
                        title="Delete Bookmark"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-theme-text-muted italic text-[11px] text-center p-2">
            No bookmarks saved. Click a location on map to save it.
          </div>
        )}
      </div>

      {/* Recent History Section */}
      <div className="border border-theme-border bg-theme-card p-4 rounded-xl flex flex-col gap-3">
        <div className="flex justify-between items-center border-b border-theme-border-sec pb-1.5">
          <span className="font-semibold text-theme-text uppercase tracking-wider text-[10px]">Recent Searches</span>
          {history.length > 0 && (
            <button
              onClick={clearHistory}
              className="text-[10px] text-theme-text-muted hover:text-theme-text cursor-pointer"
            >
              Clear
            </button>
          )}
        </div>

        {history.length > 0 ? (
          <ul className="flex flex-col gap-1.5 max-h-36 overflow-y-auto pr-1">
            {history.map((h: any) => (
              <li
                key={h.id}
                className="flex items-center justify-between gap-2 p-1.5 rounded bg-theme-btn-bg/30 hover:bg-theme-btn-bg/60 cursor-pointer"
                onClick={() => handleNavigate(h, h.name)}
              >
                <span className="truncate text-theme-text-sec hover:text-theme-text flex-1">{h.name}</span>
                <span className="text-[9px] font-mono text-theme-text-muted shrink-0">
                  {h.latitude.toFixed(3)}, {h.longitude.toFixed(3)}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-theme-text-muted italic text-[11px] text-center p-2">
            No recent search history.
          </div>
        )}
      </div>
    </div>
  )
}
