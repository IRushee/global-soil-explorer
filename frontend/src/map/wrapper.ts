import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import { MapRenderer, MapOptions, OverlayLayer } from '../types'
import { MapError } from '../utils/errors'
import { logger } from '../utils/logger'

export class MapLibreRenderer implements MapRenderer {
  private mapInstance: maplibregl.Map | null = null

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
      this.mapInstance = new maplibregl.Map({
        container: containerId,
        style: options.style || {
          version: 8,
          sources: {},
          layers: [],
        },
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

  addLayer(layer: OverlayLayer): void {
    if (!this.mapInstance) {
      logger.warn('Cannot add layer: map not initialized')
      return
    }
    logger.info(`Adding layer: ${layer.id} (${layer.type})`)
    // Core layers rendering will be implemented in Milestone 24.
  }

  updateLayer(layerId: string, updates: Partial<OverlayLayer>): void {
    if (!this.mapInstance) return
    logger.info(`Updating layer: ${layerId}`, updates)
  }

  removeLayer(layerId: string): void {
    if (!this.mapInstance) return
    logger.info(`Removing layer: ${layerId}`)
  }

  on(event: 'click' | 'zoomend' | 'moveend', handler: (e: any) => void): void {
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
    } else {
      this.mapInstance.on(event, handler)
    }
  }

  destroy(): void {
    if (this.mapInstance) {
      logger.info('Destroying MapLibre GL Map instance')
      this.mapInstance.remove()
      this.mapInstance = null
    }
  }
}

export const mapRenderer: MapRenderer = new MapLibreRenderer()
