import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { MapRenderer, MapOptions, OverlayLayer } from '../types'
import { MapError } from '../utils/errors'
import { logger } from '../utils/logger'

const BASEMAP_STYLES: Record<string, any> = {
  satellite: {
    version: 8,
    sources: {
      'satellite-tiles': {
        type: 'raster',
        tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
        tileSize: 256,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
      },
    },
    layers: [
      {
        id: 'satellite-layer',
        type: 'raster',
        source: 'satellite-tiles',
        minzoom: 0,
        maxzoom: 19,
      },
    ],
  },
  streets: {
    version: 8,
    sources: {
      'osm-tiles': {
        type: 'raster',
        tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
        tileSize: 256,
        attribution: '&copy; OpenStreetMap contributors',
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
  terrain: {
    version: 8,
    sources: {
      'terrain-tiles': {
        type: 'raster',
        tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}'],
        tileSize: 256,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri',
      },
    },
    layers: [
      {
        id: 'terrain-layer',
        type: 'raster',
        source: 'terrain-tiles',
        minzoom: 0,
        maxzoom: 19,
      },
    ],
  },
}

export class MapLibreRenderer implements MapRenderer {
  private mapInstance: maplibregl.Map | null = null
  private selectionMarker: maplibregl.Marker | null = null

  initialize(containerId: string, options: MapOptions): void {
    if (this.mapInstance) {
      logger.warn('Map already initialized on container:', containerId)
      return
    }

    logger.info(`Initializing MapLibre GL on container: ${containerId}`, options)

    // Test runner or headless fallback safety
    if (typeof window === 'undefined' || !document.getElementById(containerId)) {
      logger.warn('Container element not found or window is undefined. Map wrapper initialized in headless fallback mode.')
      return
    }

    try {
      const resolvedStyle = typeof options.style === 'string'
        ? (BASEMAP_STYLES[options.style] || BASEMAP_STYLES['satellite'])
        : (options.style || BASEMAP_STYLES['satellite'])

      this.mapInstance = new maplibregl.Map({
        container: containerId,
        style: resolvedStyle,
        center: options.center,
        zoom: options.zoom,
        maxBounds: options.maxBounds,
        trackResize: true,
      })

      this.mapInstance.on('load', () => {
        logger.info('MapLibre GL Map load complete')
      })
    } catch (e) {
      logger.error('Failed to initialize MapLibre GL Map:', e)
      throw new MapError(`Vite map wrapper load failure: ${e}`)
    }
  }

  setCenter(lat: number, lon: number): void {
    if (!this.mapInstance) {
      logger.warn('Cannot set center: map not initialized')
      return
    }
    this.mapInstance.setCenter([lon, lat])
  }

  setZoom(zoom: number): void {
    if (!this.mapInstance) {
      logger.warn('Cannot set zoom: map not initialized')
      return
    }
    this.mapInstance.setZoom(zoom)
  }

  getCenter(): [number, number] | null {
    if (!this.mapInstance) return null
    const c = this.mapInstance.getCenter()
    return [c.lng, c.lat]
  }

  getZoom(): number | null {
    if (!this.mapInstance) return null
    return this.mapInstance.getZoom()
  }

  setMaxBounds(bounds: [[number, number], [number, number]]): void {
    if (!this.mapInstance) return
    logger.info('Setting map max bounds:', bounds)
    this.mapInstance.setMaxBounds(bounds)
  }

  setBasemapStyle(basemap: string): void {
    if (!this.mapInstance) return
    logger.info(`Setting basemap style: ${basemap}`)
    const style = BASEMAP_STYLES[basemap] || BASEMAP_STYLES['satellite']
    this.mapInstance.setStyle(style)
  }

  setSelectionMarker(lat: number | null, lon: number | null): void {
    if (!this.mapInstance) return
    if (this.selectionMarker) {
      this.selectionMarker.remove()
      this.selectionMarker = null
    }
    if (lat !== null && lon !== null) {
      // Test safety if maplibregl or Marker isn't fully set up in headless
      try {
        this.selectionMarker = new maplibregl.Marker({
          color: '#06b6d4',
        })
          .setLngLat([lon, lat])
          .addTo(this.mapInstance)
      } catch (err) {
        logger.warn('Failed to add maplibregl Marker (likely running in a headless test environment):', err)
      }
    }
  }

  setCursor(cursorType: string): void {
    if (!this.mapInstance) return
    const canvas = this.mapInstance.getCanvas()
    if (canvas) {
      canvas.style.cursor = cursorType
    }
  }

  addLayer(layer: OverlayLayer): void {
    if (!this.mapInstance) {
      logger.warn('Cannot add layer: map not initialized')
      return
    }
    logger.info(`Adding layer: ${layer.id} (${layer.type})`)
    // TODO: Implement core layer rendering.
  }

  updateLayer(layerId: string, updates: Partial<OverlayLayer>): void {
    if (!this.mapInstance) return
    logger.info(`Updating layer: ${layerId}`, updates)
  }

  removeLayer(layerId: string): void {
    if (!this.mapInstance) return
    logger.info(`Removing layer: ${layerId}`)
  }

  on(event: 'click' | 'zoomend' | 'moveend' | 'mousemove', handler: (e: any) => void): void {
    if (!this.mapInstance) {
      logger.warn('Cannot bind map event listener: map not initialized')
      return
    }

    if (event === 'click') {
      this.mapInstance.on('click', (e) => {
        handler({
          coordinate: {
            latitude: e.lngLat.lat,
            longitude: e.lngLat.lng,
          },
          originalEvent: e,
        })
      })
    } else if (event === 'mousemove') {
      this.mapInstance.on('mousemove', (e) => {
        handler({
          coordinate: {
            latitude: e.lngLat.lat,
            longitude: e.lngLat.lng,
          },
          originalEvent: e,
        })
      })
    } else {
      this.mapInstance.on(event, handler)
    }
  }

  destroy(): void {
    if (this.selectionMarker) {
      this.selectionMarker.remove()
      this.selectionMarker = null
    }
    if (this.mapInstance) {
      logger.info('Destroying MapLibre GL Map instance')
      this.mapInstance.remove()
      this.mapInstance = null
    }
  }
}

export const mapRenderer: MapRenderer = new MapLibreRenderer()
