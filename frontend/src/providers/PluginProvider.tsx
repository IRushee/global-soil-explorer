import React, { useEffect } from 'react'
import { rendererRegistry, searchProvidersRegistry } from '../plugins/registry'
import { mapRenderer } from '../map/wrapper'
import { logger } from '../utils/logger'
import { NominatimSearchProvider } from '../components/SearchAndNavigation'

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
    } catch (e) {
      logger.error('Failed to initialize plugins registry:', e)
    }
  }, [])

  return <>{children}</>
}
