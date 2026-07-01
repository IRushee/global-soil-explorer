import React, { useEffect } from 'react'
import { rendererRegistry } from '../plugins/registry'
import { mapRenderer } from '../map/wrapper'
import { logger } from '../utils/logger'

export const PluginProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  useEffect(() => {
    try {
      // Register MapLibre GL Renderer wrapper automatically on application load
      if (!rendererRegistry.has('maplibre')) {
        rendererRegistry.register('maplibre', mapRenderer)
        logger.info('Auto-registered MapLibre GL Renderer in the Renderer Registry')
      }
    } catch (e) {
      logger.error('Failed to initialize plugins registry:', e)
    }
  }, [])

  return <>{children}</>
}
