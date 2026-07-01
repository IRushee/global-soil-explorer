import { StudyArea } from '../types'
import { ExtensionRegistry } from '../plugins/registry'
import { logger } from '../utils/logger'

export const studyAreaRegistry = new ExtensionRegistry<string, StudyArea>()

// Default Study Areas Registration
const worldStudyArea: StudyArea = {
  id: 'world',
  name: 'Global HWSD Grid',
  projection: 'EPSG:4326',
  bounds: [
    [-180, -90],
    [180, 90],
  ],
  availableDatasets: ['hwsd_v2'],
  defaultZoom: 2,
  maxZoom: 18,
  availableBasemaps: ['satellite', 'terrain', 'streets'],
  tileEndpoint: '/tiles/world/{z}/{x}/{y}.mvt',
  apiEndpoint: '/v1/soil',
  plugins: [],
  capabilities: {
    supportsProfiles: true,
    supportsLayers: true,
    supportsTexture: true,
    supportsChemistry: true,
    supportsHydrology: true,
    supportsRaster: true,
    supportsVectorTiles: true,
    supportsOffline: true,
    supportsSearch: true,
    supportsExport: true,
  },
}

const indiaStudyArea: StudyArea = {
  id: 'india',
  name: 'India Regional Grid',
  projection: 'EPSG:4326',
  bounds: [
    [68.1, 6.7],
    [97.4, 35.5],
  ],
  availableDatasets: ['hwsd_v2', 'soilgrids'],
  defaultZoom: 5,
  maxZoom: 16,
  availableBasemaps: ['satellite', 'streets'],
  tileEndpoint: '/tiles/india/{z}/{x}/{y}.mvt',
  apiEndpoint: '/v1/soil',
  plugins: [],
  capabilities: {
    supportsProfiles: true,
    supportsLayers: true,
    supportsTexture: true,
    supportsChemistry: true,
    supportsHydrology: true,
    supportsRaster: true,
    supportsVectorTiles: false,
    supportsOffline: true,
    supportsSearch: true,
    supportsExport: true,
  },
}

try {
  studyAreaRegistry.register('world', worldStudyArea)
  studyAreaRegistry.register('india', indiaStudyArea)
  logger.info('Registered default study areas (world, india)')
} catch (e) {
  logger.error('Failed to register default study areas:', e)
}
