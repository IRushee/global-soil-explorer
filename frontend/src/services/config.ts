import { AppConfiguration, ConfigurationService } from '../types'
import { ConfigurationError } from '../utils/errors'
import { logger } from '../utils/logger'

class ConfigurationServiceImpl implements ConfigurationService {
  private config: AppConfiguration

  constructor() {
    try {
      const isTest = typeof process !== 'undefined' && process.env && process.env.NODE_ENV === 'test'
      const envSource = isTest ? process.env : (import.meta.env || {})

      const environment = (envSource.VITE_USER_ENV || envSource.NODE_ENV || 'development') as 'development' | 'production' | 'test'
      const apiBaseUrl = (envSource.VITE_API_BASE_URL || 'http://localhost:8000/v1') as string
      const tileBaseUrl = (envSource.VITE_TILE_BASE_URL || 'http://localhost:8000/v1/tiles') as string

      this.config = {
        environment,
        activeStudyAreaId: 'world',
        activeDatasetId: 'hwsd_v2',
        activeRendererId: 'maplibre',
        enabledPlugins: [],
        featureFlags: {
          FLAG_ANALYSIS_TOOLS: (envSource.VITE_FLAG_ANALYSIS_TOOLS === 'true'),
          FLAG_OFFLINE_MODE: (envSource.VITE_FLAG_OFFLINE_MODE === 'true'),
          FLAG_TERRAIN_3D: (envSource.VITE_FLAG_TERRAIN_3D === 'true'),
          FLAG_EXPORT_PDF: (envSource.VITE_FLAG_EXPORT_PDF === 'true'),
          FLAG_WORKSPACES: (envSource.VITE_FLAG_WORKSPACES === 'true'),
        },
        apiBaseUrl,
        tileBaseUrl,
      }

      logger.info('ConfigurationService initialized successfully', { env: this.config.environment })
    } catch (e) {
      throw new ConfigurationError(`Failed to initialize configuration service: ${e}`)
    }
  }

  get(): AppConfiguration {
    return this.config
  }

  isFeatureEnabled(flagName: string): boolean {
    return !!this.config.featureFlags[flagName]
  }

  updateActiveStudyArea(studyAreaId: string): void {
    logger.info(`Updating active study area to: ${studyAreaId}`)
    this.config.activeStudyAreaId = studyAreaId
  }

  updateActiveDataset(datasetId: string): void {
    logger.info(`Updating active dataset to: ${datasetId}`)
    this.config.activeDatasetId = datasetId
  }
}

export const configService: ConfigurationService = new ConfigurationServiceImpl()
