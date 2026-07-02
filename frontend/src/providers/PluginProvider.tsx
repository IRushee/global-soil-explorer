import React, { useEffect } from 'react'
import { rendererRegistry, searchProvidersRegistry, overlayLayersRegistry } from '../plugins/registry'
import { mapRenderer } from '../map/wrapper'
import { logger } from '../utils/logger'
import { NominatimSearchProvider } from '../components/SearchAndNavigation'
import { OverlayLayer } from '../types'
import { useGlobalStore } from '../store'

export const PluginProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  useEffect(() => {
    try {
      // Register MapLibre GL Renderer wrapper automatically on application load
      if (!rendererRegistry.has('maplibre')) {
        rendererRegistry.register('maplibre', mapRenderer)
        logger.info('Auto-registered MapLibre GL Renderer in the Renderer Registry')
      }

      // Register Nominatim search provider automatically on application load
      if (!searchProvidersRegistry.has('nominatim')) {
        searchProvidersRegistry.register('nominatim', new NominatimSearchProvider())
        logger.info('Auto-registered Nominatim Search Provider in the Search Providers Registry')
      }

      // Register Thematic Soil Layers
      const thematicLayers: OverlayLayer[] = [
        {
          id: 'hwsd_texture',
          title: 'Soil Texture (USDA)',
          description: 'Distribution of sand, silt, and clay fractions.',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/texture/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'categorical', title: 'Soil Texture Class', unit: 'Class', colors: ['#f59e0b', '#ca8a04', '#713f12'], labels: ['Sandy', 'Loamy', 'Clayey'] }
        },
        {
          id: 'hwsd_ph',
          title: 'Soil pH (H₂O)',
          description: 'Topsoil pH measurement (acidity/alkalinity).',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/ph/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'continuous', title: 'pH Scale', unit: 'pH', colors: ['#ef4444', '#f59e0b', '#eab308', '#10b981', '#3b82f6'], labels: ['4.0', '7.0', '9.0'] }
        },
        {
          id: 'hwsd_oc',
          title: 'Organic Carbon',
          description: 'Organic carbon density in topsoil (0-30 cm).',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/oc/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'continuous', title: 'Organic Carbon', unit: '%', colors: ['#fef08a', '#ca8a04', '#713f12'], labels: ['0%', '2.5%', '>5%'] }
        },
        {
          id: 'hwsd_bd',
          title: 'Bulk Density',
          description: 'Reference bulk density of soil layer.',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/bd/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'continuous', title: 'Bulk Density', unit: 'g/cm³', colors: ['#eff6ff', '#60a5fa', '#1e3a8a'], labels: ['0.8', '1.3', '1.8'] }
        },
        {
          id: 'hwsd_coarse',
          title: 'Coarse Fragments',
          description: 'Percentage of gravels and stones in soil layer.',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/coarse/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'continuous', title: 'Coarse Fragments', unit: '%', colors: ['#fff7ed', '#ffedd5', '#fed7aa', '#fdbb2d', '#ea580c'], labels: ['0%', '20%', '40%', '60%', '>80%'] }
        },
        {
          id: 'hwsd_cec',
          title: 'Cation Exchange Capacity (CEC)',
          description: 'Soil nutrient holding capacity.',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/cec/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'continuous', title: 'CEC Soil', unit: 'cmol/kg', colors: ['#f3e8ff', '#c084fc', '#581c87'], labels: ['0', '24', '>48'] }
        },
        {
          id: 'hwsd_bs',
          title: 'Base Saturation',
          description: 'Percentage of CEC occupied by basic cations.',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/bs/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'continuous', title: 'Base Saturation', unit: '%', colors: ['#ecfdf5', '#34d399', '#065f46'], labels: ['0%', '50%', '100%'] }
        },
        {
          id: 'hwsd_drainage',
          title: 'Soil Drainage Class',
          description: 'Natural drainage rate and soil wetness.',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/drainage/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'categorical', title: 'Drainage Class', unit: 'Class', colors: ['#fee2e2', '#bfdbfe', '#2563eb'], labels: ['Poorly', 'Moderately', 'Well'] }
        },
        {
          id: 'hwsd_wrb',
          title: 'WRB Soil Reference Groups',
          description: 'World Reference Base classification map.',
          dataset: 'HWSD v2.0',
          renderer: 'maplibre',
          type: 'vector',
          sourceUrl: '/tiles/world/wrb/{z}/{x}/{y}.mvt',
          visible: false,
          opacity: 0.75,
          minZoom: 0,
          maxZoom: 18,
          queryable: true,
          downloadable: true,
          exportable: true,
          cachePolicy: { maxAgeSeconds: 3600, persist: true },
          refreshPolicy: 'never',
          dependencies: [],
          legend: { type: 'categorical', title: 'WRB Reference Group', unit: 'Group', colors: ['#fbcfe8', '#db2777', '#4c0519'], labels: ['Luvisol', 'Cambisol', 'Fluvisol'] }
        }
      ]

      thematicLayers.forEach(layer => {
        if (!overlayLayersRegistry.has(layer.id)) {
          overlayLayersRegistry.register(layer.id, layer)
        }
      })

      // Sync registered layers to global Zustand store
      const registeredLayers = overlayLayersRegistry.list().map(id => overlayLayersRegistry.get(id))
      useGlobalStore.getState().setOverlays(registeredLayers)

    } catch (e) {
      logger.error('Failed to initialize plugins registry:', e)
    }
  }, [])

  return <>{children}</>
}
