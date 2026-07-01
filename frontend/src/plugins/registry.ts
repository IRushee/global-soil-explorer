import {
  ScientificDatasetTranslator,
  SearchProvider,
  ExportProvider,
  MapRenderer,
  OverlayLayer,
} from '../types'
import { PluginError } from '../utils/errors'
import { logger } from '../utils/logger'

export class ExtensionRegistry<K, P> {
  private providers: Map<K, P> = new Map()

  register(key: K, provider: P): void {
    if (this.providers.has(key)) {
      throw new PluginError(`Provider already registered: ${String(key)}`)
    }
    this.providers.set(key, provider)
    logger.info(`Registered provider for key: ${String(key)}`)
  }

  get(key: K): P {
    const provider = this.providers.get(key)
    if (!provider) {
      throw new PluginError(`Provider not found: ${String(key)}`)
    }
    return provider
  }

  list(): K[] {
    return Array.from(this.providers.keys())
  }

  has(key: K): boolean {
    return this.providers.has(key)
  }

  unregister(key: K): void {
    if (this.providers.has(key)) {
      this.providers.delete(key)
      logger.info(`Unregistered provider for key: ${String(key)}`)
    }
  }
}

// Global Registries
export const datasetTranslatorsRegistry = new ExtensionRegistry<string, ScientificDatasetTranslator>()
export const searchProvidersRegistry = new ExtensionRegistry<string, SearchProvider>()
export const exportProvidersRegistry = new ExtensionRegistry<string, ExportProvider>()
export const rendererRegistry = new ExtensionRegistry<string, MapRenderer>()
export const overlayLayersRegistry = new ExtensionRegistry<string, OverlayLayer>()
export const basemapProvidersRegistry = new ExtensionRegistry<string, { id: string; name: string; url: string }>()
export const analysisProvidersRegistry = new ExtensionRegistry<string, { id: string; run(data: any): any }>()
