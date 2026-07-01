export interface Coordinate {
  latitude: number
  longitude: number
}

export interface EnvironmentalContext {
  koppen_climate?: string | null
}

export interface DatasetMetadataCodes {
  coverage?: number | null
}

export interface DatasetMetadata {
  coverage_description?: string | null
  library?: string | null
  source?: string | null
  dataset_version?: string | null
  reference_identifiers?: string[][] | null
  codes: DatasetMetadataCodes
}

export interface SoilClassificationCodes {
  class_symbol: string
  wrb4_code?: string | null
  wrb2_code?: string | null
  fao90_code?: string | null
  wrb_phase_code?: string | null
  dominant_group_code?: string | null
}

export interface SoilClassification {
  taxonomy_standard: string
  class_name: string
  wrb4_name?: string | null
  wrb2_name?: string | null
  fao90_name?: string | null
  wrb_phase_name?: string | null
  national_classification?: string | null
  codes: SoilClassificationCodes
}

export interface HydrologicContextCodes {
  drainage?: string | null
  water_regime?: number | null
  impermeable_layer?: number | null
}

export interface HydrologicContext {
  drainage_description?: string | null
  water_regime_description?: string | null
  impermeable_layer_description?: string | null
  codes: HydrologicContextCodes
}

export interface LandLimitationsCodes {
  root_depth?: number | null
  root_obstacles?: number | null
  phase1?: number | null
  phase2?: number | null
  additional_property?: number | null
}

export interface LandLimitations {
  root_depth_description?: string | null
  root_obstacles_description?: string | null
  phase1_description?: string | null
  phase2_description?: string | null
  additional_property_description?: string | null
  codes: LandLimitationsCodes
}

export interface SoilTextureCodes {
  usda_texture?: number | null
  soter_texture?: string | null
}

export interface SoilTexture {
  usda_texture_description?: string | null
  soter_texture_description?: string | null
  codes: SoilTextureCodes
}

export interface PhysicalProperties {
  sand?: number | null
  silt?: number | null
  clay?: number | null
  coarse_fragments?: number | null
  bulk_density?: number | null
  ref_bulk_density?: number | null
}

export interface ChemicalProperties {
  ph?: number | null
  organic_carbon?: number | null
  total_nitrogen?: number | null
  cn_ratio?: number | null
  cec_soil?: number | null
  cec_clay?: number | null
  effective_cec?: number | null
  teb?: number | null
  base_saturation?: number | null
  aluminum_saturation?: number | null
  esp?: number | null
  calcium_carbonate?: number | null
  gypsum?: number | null
  electrical_conductivity?: number | null
}

export interface HydraulicProperties {
  available_water_capacity?: number | null
}

export interface LayerMeasurements {
  physical: PhysicalProperties
  chemical: ChemicalProperties
  hydraulic: HydraulicProperties
}

export interface SoilProperty {
  property_type: string
  value: number
  unit: string
}

export interface SoilLayer {
  top_depth_cm: number
  bottom_depth_cm: number
  properties: SoilProperty[]
  texture?: SoilTexture | null
  measurements?: LayerMeasurements | null
}

export interface SoilProfile {
  composition_share?: number | null
  sequence_index?: number | null
  classification: SoilClassification
  hydrologic_context?: HydrologicContext | null
  land_limitations?: LandLimitations | null
  layers: SoilLayer[]
}

export interface SoilObservation {
  coordinate: Coordinate
  profiles: SoilProfile[]
  environmental_context?: EnvironmentalContext | null
  metadata?: DatasetMetadata | null
}

// Map Interface Constants
export type LegendConfig = Record<string, any>
export type StyleRule = Record<string, any>

export interface OverlayLayer {
  id: string
  title: string
  description: string
  dataset: string
  renderer: string
  type: 'raster' | 'vector' | 'geojson'
  sourceUrl: string
  visible: boolean
  opacity: number
  minZoom: number
  maxZoom: number
  queryable: boolean
  downloadable: boolean
  exportable: boolean
  cachePolicy: {
    maxAgeSeconds: number
    persist: boolean
  }
  refreshPolicy: 'on_mount' | 'manual' | 'never'
  dependencies: string[]
  legend: LegendConfig
}

export interface DatasetCapabilities {
  supportsProfiles: boolean
  supportsLayers: boolean
  supportsTexture: boolean
  supportsChemistry: boolean
  supportsHydrology: boolean
  supportsRaster: boolean
  supportsVectorTiles: boolean
  supportsOffline: boolean
  supportsSearch: boolean
  supportsExport: boolean
}

export interface DatasetManifest {
  id: string
  name: string
  version: string
  provider: string
  license: string
  citation: string
  projection: string
  coverage: string
  resolution: string
  depthIntervals: { top: number; bottom: number }[]
  availableProperties: string[]
  availableLayers: string[]
  lastUpdated: string
  supportedExports: string[]
  colorScheme: Record<string, string>
  studyAreas: string[]
}

export interface RendererCapabilities {
  supportsVectorTiles: boolean
  supportsRaster: boolean
  supports3D: boolean
  supportsTerrain: boolean
  supportsOffline: boolean
  supportsOpacity: boolean
  supportsAnimation: boolean
}

export interface MapOptions {
  container: string
  style: any
  center: [number, number]
  zoom: number
  maxBounds?: [[number, number], [number, number]]
}

export interface MapRenderer {
  initialize(containerId: string, options: MapOptions): void
  setCenter(lat: number, lon: number): void
  setZoom(zoom: number): void
  getCenter(): [number, number] | null
  getZoom(): number | null
  setMaxBounds(bounds: [[number, number], [number, number]]): void
  setBasemapStyle(basemap: string): void
  setCursor(cursorType: string): void
  setSelectionMarker(lat: number | null, lon: number | null): void
  flyTo(lat: number, lon: number, zoom?: number): void
  addLayer(layer: OverlayLayer): void
  updateLayer(layerId: string, updates: Partial<OverlayLayer>): void
  removeLayer(layerId: string): void
  on(event: 'click' | 'zoomend' | 'moveend' | 'mousemove', handler: (e: any) => void): void
  destroy(): void
}

export interface StudyArea {
  id: string
  name: string
  projection: string
  bounds: [[number, number], [number, number]]
  availableDatasets: string[]
  defaultZoom: number
  maxZoom: number
  availableBasemaps: string[]
  tileEndpoint: string
  apiEndpoint: string
  plugins: string[]
  capabilities: DatasetCapabilities
}

// Commands
export interface Command {
  id: string
  timestamp: number
  execute(): void
  undo(): void
}

// Events
export type AppEventType =
  | 'CoordinateSelected'
  | 'ObservationLoaded'
  | 'LayerChanged'
  | 'BasemapChanged'
  | 'DatasetChanged'
  | 'FilterChanged'
  | 'ExportRequested'
  | 'SearchCompleted'
  | 'StudyAreaChanged'

export interface AppEvent<T = any> {
  type: AppEventType
  payload: T
  timestamp: number
}

// Search
export interface SearchResultItem {
  id: string
  label: string
  category: 'coordinate' | 'location' | 'scientific_attribute' | 'dataset' | 'bookmark' | 'history'
  coordinate: { lat: number; lon: number }
  score: number
  metadata?: Record<string, any>
}

export interface SearchProvider {
  id: string
  name: string
  search(query: string, bounds?: [[number, number], [number, number]]): Promise<SearchResultItem[]>
}

// Export
export interface ExportResult {
  success: boolean
  url?: string
  blob?: Blob
  error?: string
}

export interface ExportProvider {
  format: 'json' | 'csv' | 'geojson' | 'pdf' | 'png' | 'clipboard' | 'share'
  export(observation: SoilObservation, metadata?: Record<string, any>): Promise<ExportResult>
}

// Translators
export interface ScientificDatasetTranslator {
  id: string
  translate(rawData: any): SoilObservation
}

// Configuration
export interface AppConfiguration {
  environment: 'development' | 'production' | 'test'
  activeStudyAreaId: string
  activeDatasetId: string
  activeRendererId: string
  enabledPlugins: string[]
  featureFlags: Record<string, boolean>
  apiBaseUrl: string
  tileBaseUrl: string
}

export interface ConfigurationService {
  get(): AppConfiguration
  isFeatureEnabled(flagName: string): boolean
  updateActiveStudyArea(studyAreaId: string): void
  updateActiveDataset(datasetId: string): void
}

