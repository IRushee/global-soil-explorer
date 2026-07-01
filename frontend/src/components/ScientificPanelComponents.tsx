import React from 'react'
import { SoilObservation, Coordinate, SoilProfile, SoilLayer, DatasetMetadata } from '../types'

// 1. ObservationSummary
interface ObservationSummaryProps {
  observation: SoilObservation
  selectedCoordinate: Coordinate
  datasetId: string
}

export const ObservationSummary: React.FC<ObservationSummaryProps> = ({
  observation,
  selectedCoordinate,
  datasetId,
}) => {
  const profileCount = observation.profiles?.length || 0
  const coverage = observation.metadata?.coverage_description || 'Global Coverage'
  const version = observation.metadata?.dataset_version || 'v2.0'
  const source = observation.metadata?.source || 'HWSD'

  return (
    <div className="border border-slate-800 bg-slate-900/50 p-4 rounded-lg flex flex-col gap-3 shadow-md">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Observation Summary</span>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950/40 text-emerald-400 border border-emerald-900/50 font-medium">
          Resolved
        </span>
      </div>
      <div className="grid grid-cols-2 gap-x-4 gap-y-2 text-xs leading-relaxed">
        <div className="flex flex-col">
          <span className="text-slate-500">Latitude</span>
          <span className="font-mono text-slate-300">{selectedCoordinate.latitude.toFixed(6)}°</span>
        </div>
        <div className="flex flex-col">
          <span className="text-slate-500">Longitude</span>
          <span className="font-mono text-slate-300">{selectedCoordinate.longitude.toFixed(6)}°</span>
        </div>
        <div className="flex flex-col col-span-2 pt-1 border-t border-slate-850/50">
          <span className="text-slate-500">Dataset</span>
          <span className="text-slate-350 font-medium uppercase">{datasetId.replace('_', ' ')} (v{version})</span>
        </div>
        <div className="flex flex-col">
          <span className="text-slate-500">Profiles Found</span>
          <span className="text-slate-300">{profileCount} {profileCount === 1 ? 'profile' : 'profiles'}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-slate-500">Source</span>
          <span className="text-slate-300 italic">{source}</span>
        </div>
        <div className="col-span-2 flex flex-col pt-1 border-t border-slate-850/50">
          <span className="text-slate-500">Coverage Description</span>
          <span className="text-slate-300 text-[11px]">{coverage}</span>
        </div>
      </div>
    </div>
  )
}

// 2. ProfileSelector
interface ProfileSelectorProps {
  profiles: SoilProfile[]
  activeIndex: number
  onChange: (index: number) => void
}

export const ProfileSelector: React.FC<ProfileSelectorProps> = ({
  profiles,
  activeIndex,
  onChange,
}) => {
  if (!profiles || profiles.length <= 1) return null

  return (
    <div className="flex flex-col gap-2">
      <span className="text-xs font-semibold text-slate-400 tracking-wide">Mapping Unit Components:</span>
      <div className="flex flex-wrap gap-1.5 border-b border-slate-800 pb-3">
        {profiles.map((profile, idx) => {
          const shareVal = profile.composition_share !== null && profile.composition_share !== undefined
            ? (profile.composition_share <= 1 ? Math.round(profile.composition_share * 100) : Math.round(profile.composition_share))
            : null
          const shareStr = shareVal !== null ? ` (${shareVal}%)` : ''
          const name = profile.classification.class_name
          const isActive = idx === activeIndex
          return (
            <button
              key={idx}
              onClick={() => onChange(idx)}
              className={`text-xs px-3 py-1.5 rounded-md transition-all font-medium border ${
                isActive
                  ? 'bg-teal-950/30 text-teal-400 border-teal-800/80 shadow-md font-semibold'
                  : 'bg-slate-800/40 text-slate-400 border-transparent hover:bg-slate-800 hover:text-slate-200'
              }`}
            >
              {name}{shareStr}
            </button>
          )
        })}
      </div>
    </div>
  )
}

// 3. LayerCard
interface LayerCardProps {
  layer: SoilLayer
  index: number
  isActive: boolean
  onClick: () => void
}

export const LayerCard: React.FC<LayerCardProps> = ({
  layer,
  index,
  isActive,
  onClick,
}) => {
  const getPropertyValue = (layer: any, type: string): number | null => {
    if (layer.measurements) {
      if (type === 'ph') return layer.measurements.chemical?.ph ?? null
      if (type === 'organic_carbon') return layer.measurements.chemical?.organic_carbon ?? null
    }
    if (layer.properties && Array.isArray(layer.properties)) {
      const prop = layer.properties.find((p: any) => p.property_type.toLowerCase() === type.toLowerCase())
      return prop ? prop.value : null
    }
    return null
  }

  const ph = getPropertyValue(layer, 'ph')
  const oc = getPropertyValue(layer, 'organic_carbon')

  return (
    <div
      onClick={onClick}
      className={`border rounded-lg p-3.5 flex flex-col gap-2 transition-all cursor-pointer select-none shadow-sm ${
        isActive
          ? 'bg-teal-950/20 border-teal-800/80 shadow-md ring-1 ring-teal-900/50'
          : 'bg-slate-900/30 border-slate-800 hover:border-slate-700 hover:bg-slate-800/20'
      }`}
    >
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-semibold text-slate-500">#{index + 1}</span>
          <span className="font-semibold text-slate-200 text-sm">
            {layer.top_depth_cm} - {layer.bottom_depth_cm} cm
          </span>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">
          {layer.bottom_depth_cm - layer.top_depth_cm} cm thick
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs text-slate-400">
        <div>
          <span className="text-slate-500">pH (H₂O):</span>{' '}
          <span className="font-mono font-semibold text-slate-300">
            {ph !== null ? ph.toFixed(2) : 'N/A'}
          </span>
        </div>
        <div>
          <span className="text-slate-500">Org. Carbon:</span>{' '}
          <span className="font-mono font-semibold text-slate-300">
            {oc !== null ? `${oc.toFixed(2)}%` : 'N/A'}
          </span>
        </div>
      </div>
    </div>
  )
}

// 4. LayerList
interface LayerListProps {
  layers: SoilLayer[]
  activeLayerIndex: number | null
  onLayerSelect: (index: number | null) => void
}

export const LayerList: React.FC<LayerListProps> = ({
  layers,
  activeLayerIndex,
  onLayerSelect,
}) => {
  if (!layers || layers.length === 0) {
    return <div className="text-xs text-slate-500 italic">No depth layers available.</div>
  }

  return (
    <div className="flex flex-col gap-2.5">
      <span className="text-xs font-semibold text-slate-400 tracking-wide">Soil Layers (Horizons):</span>
      <div className="flex flex-col gap-2">
        {layers.map((layer, idx) => (
          <LayerCard
            key={idx}
            layer={layer}
            index={idx}
            isActive={idx === activeLayerIndex}
            onClick={() => onLayerSelect(idx === activeLayerIndex ? null : idx)}
          />
        ))}
      </div>
    </div>
  )
}

// 5. ScientificPropertyTable
interface ScientificPropertyTableProps {
  layer: SoilLayer
}

export const ScientificPropertyTable: React.FC<ScientificPropertyTableProps> = ({ layer }) => {
  const getPropertyValue = (layer: any, path: string[], fallbackName: string): { value: number | null; unit: string } => {
    let current = layer
    for (const key of path) {
      if (current && typeof current === 'object') {
        current = current[key]
      } else {
        current = undefined
        break
      }
    }
    if (current !== undefined && current !== null) {
      const unit = layer.properties?.find((p: any) => p.property_type.toLowerCase() === fallbackName.toLowerCase())?.unit || ''
      return { value: current as number, unit }
    }
    const prop = layer.properties?.find((p: any) => p.property_type.toLowerCase() === fallbackName.toLowerCase())
    if (prop) {
      return { value: prop.value, unit: prop.unit }
    }
    return { value: null, unit: '' }
  }

  // Physical Properties
  const sand = getPropertyValue(layer, ['measurements', 'physical', 'sand'], 'sand')
  const silt = getPropertyValue(layer, ['measurements', 'physical', 'silt'], 'silt')
  const clay = getPropertyValue(layer, ['measurements', 'physical', 'clay'], 'clay')
  const coarse = getPropertyValue(layer, ['measurements', 'physical', 'coarse_fragments'], 'coarse_fragments')
  const bd = getPropertyValue(layer, ['measurements', 'physical', 'bulk_density'], 'bulk_density')
  const rbd = getPropertyValue(layer, ['measurements', 'physical', 'ref_bulk_density'], 'ref_bulk_density')

  // Chemical Properties
  const ph = getPropertyValue(layer, ['measurements', 'chemical', 'ph'], 'ph')
  const oc = getPropertyValue(layer, ['measurements', 'chemical', 'organic_carbon'], 'organic_carbon')
  const tn = getPropertyValue(layer, ['measurements', 'chemical', 'total_nitrogen'], 'total_nitrogen')
  const cn = getPropertyValue(layer, ['measurements', 'chemical', 'cn_ratio'], 'cn_ratio')
  const cecSoil = getPropertyValue(layer, ['measurements', 'chemical', 'cec_soil'], 'cec_soil')
  const cecClay = getPropertyValue(layer, ['measurements', 'chemical', 'cec_clay'], 'cec_clay')
  const bs = getPropertyValue(layer, ['measurements', 'chemical', 'base_saturation'], 'base_saturation')
  const ec = getPropertyValue(layer, ['measurements', 'chemical', 'electrical_conductivity'], 'electrical_conductivity')
  const caco3 = getPropertyValue(layer, ['measurements', 'chemical', 'calcium_carbonate'], 'calcium_carbonate')
  const gypsum = getPropertyValue(layer, ['measurements', 'chemical', 'gypsum'], 'gypsum')

  // Hydraulic Properties
  const awc = getPropertyValue(layer, ['measurements', 'hydraulic', 'available_water_capacity'], 'available_water_capacity')

  const formatVal = (v: number | null, unit: string) => {
    if (v === null) return 'N/A'
    return `${v.toFixed(2)}${unit ? ' ' + unit : ''}`
  }

  return (
    <div className="border border-slate-800 bg-slate-900/30 rounded-lg p-4 flex flex-col gap-4 shadow-sm">
      <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider border-b border-slate-800 pb-1.5">
        Horizon Measurements ({layer.top_depth_cm} - {layer.bottom_depth_cm} cm)
      </span>

      {/* Texture Display */}
      {(sand.value !== null || silt.value !== null || clay.value !== null) && (
        <div className="flex flex-col gap-1.5 pb-3 border-b border-slate-855/55">
          <span className="text-slate-450 font-medium text-xs">Soil Texture Fractions:</span>
          <div className="flex w-full h-3 rounded-full overflow-hidden bg-slate-800/85 border border-slate-750">
            {sand.value !== null && (
              <div style={{ width: `${sand.value}%` }} className="bg-amber-500 h-full" title={`Sand: ${sand.value}%`} />
            )}
            {silt.value !== null && (
              <div style={{ width: `${silt.value}%` }} className="bg-slate-450 h-full" title={`Silt: ${silt.value}%`} />
            )}
            {clay.value !== null && (
              <div style={{ width: `${clay.value}%` }} className="bg-red-500 h-full" title={`Clay: ${clay.value}%`} />
            )}
          </div>
          <div className="flex justify-between text-[10px] font-mono text-slate-450">
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block"></span>
              Sand: {sand.value !== null ? `${sand.value.toFixed(1)}%` : 'N/A'}
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-450 inline-block"></span>
              Silt: {silt.value !== null ? `${silt.value.toFixed(1)}%` : 'N/A'}
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block"></span>
              Clay: {clay.value !== null ? `${clay.value.toFixed(1)}%` : 'N/A'}
            </span>
          </div>
        </div>
      )}

      {/* Grid Table of Attributes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs leading-relaxed">
        {/* Physical block */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Physical Properties</span>
          <div className="flex justify-between border-b border-slate-850/50 pb-1">
            <span className="text-slate-450">Bulk Density:</span>
            <span className="font-mono text-slate-200">{formatVal(bd.value, bd.unit || 'g/cm³')}</span>
          </div>
          <div className="flex justify-between border-b border-slate-855 pb-1">
            <span className="text-slate-450">Ref Bulk Density:</span>
            <span className="font-mono text-slate-200">{formatVal(rbd.value, rbd.unit || 'g/cm³')}</span>
          </div>
          <div className="flex justify-between border-b border-slate-855 pb-1">
            <span className="text-slate-450">Coarse Fragments:</span>
            <span className="font-mono text-slate-200">{formatVal(coarse.value, coarse.unit || '%')}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-450">Available Water:</span>
            <span className="font-mono text-slate-200">{formatVal(awc.value, awc.unit || '%')}</span>
          </div>
        </div>

        {/* Chemical block */}
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Chemical Properties</span>
          <div className="flex justify-between border-b border-slate-850/50 pb-1">
            <span className="text-slate-450">pH (H₂O):</span>
            <span className="font-mono text-slate-200">{ph.value !== null ? ph.value.toFixed(2) : 'N/A'}</span>
          </div>
          <div className="flex justify-between border-b border-slate-855 pb-1">
            <span className="text-slate-450">Organic Carbon:</span>
            <span className="font-mono text-slate-200">{formatVal(oc.value, oc.unit || '%')}</span>
          </div>
          <div className="flex justify-between border-b border-slate-855 pb-1">
            <span className="text-slate-450">Total Nitrogen:</span>
            <span className="font-mono text-slate-200">{formatVal(tn.value, tn.unit || '%')}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-450">C/N Ratio:</span>
            <span className="font-mono text-slate-200">{formatVal(cn.value, cn.unit)}</span>
          </div>
        </div>

        {/* Extra Chemical block */}
        <div className="col-span-1 sm:col-span-2 flex flex-col gap-1.5 pt-2 border-t border-slate-800">
          <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">CEC & Exchange Complex</span>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <div className="flex justify-between border-b border-slate-855 pb-1 sm:pb-0.5">
              <span className="text-slate-450">CEC Soil:</span>
              <span className="font-mono text-slate-200">{formatVal(cecSoil.value, cecSoil.unit || 'cmol/kg')}</span>
            </div>
            <div className="flex justify-between border-b border-slate-855 pb-1 sm:pb-0.5">
              <span className="text-slate-450">CEC Clay:</span>
              <span className="font-mono text-slate-200">{formatVal(cecClay.value, cecClay.unit || 'cmol/kg')}</span>
            </div>
            <div className="flex justify-between border-b border-slate-855 pb-1 sm:border-none sm:pb-0">
              <span className="text-slate-450">Base Saturation:</span>
              <span className="font-mono text-slate-200">{formatVal(bs.value, bs.unit || '%')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-450">Elec. Conductivity (EC):</span>
              <span className="font-mono text-slate-200">{formatVal(ec.value, ec.unit || 'dS/m')}</span>
            </div>
          </div>
        </div>

        {/* Minerals block */}
        {(caco3.value !== null || gypsum.value !== null) && (
          <div className="col-span-1 sm:col-span-2 flex flex-col gap-1.5 pt-2 border-t border-slate-800">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Salts & Carbonates</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1 text-xs">
              <div className="flex justify-between border-b border-slate-855 pb-1 sm:border-none sm:pb-0">
                <span className="text-slate-450">Calcium Carbonate:</span>
                <span className="font-mono text-slate-200">{formatVal(caco3.value, caco3.unit || '%')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-450">Gypsum:</span>
                <span className="font-mono text-slate-200">{formatVal(gypsum.value, gypsum.unit || '%')}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// 6. ClassificationCard
interface ClassificationCardProps {
  profile: SoilProfile
}

export const ClassificationCard: React.FC<ClassificationCardProps> = ({ profile }) => {
  const classification = profile.classification
  const hydro = profile.hydrologic_context
  const limitations = profile.land_limitations

  return (
    <div className="border border-slate-800 bg-slate-900/30 rounded-lg p-4 flex flex-col gap-4 shadow-sm">
      <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider border-b border-slate-800 pb-1.5">
        Soil Classification & Context
      </span>

      {/* Taxonomy Section */}
      <div className="flex flex-col gap-1.5">
        <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Taxonomic Name</span>
        <div className="text-slate-200 font-semibold text-sm">{classification.class_name}</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-400 mt-1">
          {classification.taxonomy_standard && (
            <div>
              <span className="text-slate-500">Standard:</span> {classification.taxonomy_standard}
            </div>
          )}
          {classification.codes.class_symbol && (
            <div>
              <span className="text-slate-500">Symbol Code:</span> {classification.codes.class_symbol}
            </div>
          )}
          {classification.wrb4_name && (
            <div className="col-span-1 sm:col-span-2">
              <span className="text-slate-500">WRB 2022 (4th Ed):</span> {classification.wrb4_name}
            </div>
          )}
          {classification.wrb2_name && (
            <div className="col-span-1 sm:col-span-2">
              <span className="text-slate-500">WRB 2006 (2nd Ed):</span> {classification.wrb2_name}
            </div>
          )}
          {classification.fao90_name && (
            <div className="col-span-1 sm:col-span-2">
              <span className="text-slate-500">FAO 1990:</span> {classification.fao90_name}
            </div>
          )}
          {classification.wrb_phase_name && (
            <div className="col-span-1 sm:col-span-2">
              <span className="text-slate-500">WRB Phase:</span> {classification.wrb_phase_name}
            </div>
          )}
        </div>
      </div>

      {/* Hydrology Section */}
      {hydro && (
        <div className="flex flex-col gap-1.5 pt-2.5 border-t border-slate-800">
          <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Hydrologic Context</span>
          <div className="flex flex-col gap-1 text-xs text-slate-300">
            {hydro.drainage_description && (
              <div>
                <span className="text-slate-500">Drainage Class:</span> {hydro.drainage_description}
              </div>
            )}
            {hydro.water_regime_description && (
              <div>
                <span className="text-slate-500">Water Regime:</span> {hydro.water_regime_description}
              </div>
            )}
            {hydro.impermeable_layer_description && (
              <div>
                <span className="text-slate-500">Impermeable Horizon:</span> {hydro.impermeable_layer_description}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Land Limitations Section */}
      {limitations && (
        <div className="flex flex-col gap-1.5 pt-2.5 border-t border-slate-800">
          <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Limiting Factors</span>
          <div className="flex flex-col gap-1 text-xs text-slate-355">
            {limitations.root_depth_description && (
              <div>
                <span className="text-slate-500">Root Depth Limit:</span> {limitations.root_depth_description}
              </div>
            )}
            {limitations.root_obstacles_description && (
              <div>
                <span className="text-slate-500">Root Obstacles:</span> {limitations.root_obstacles_description}
              </div>
            )}
            {limitations.phase1_description && (
              <div>
                <span className="text-slate-500">Phase 1 (Characteristics):</span> {limitations.phase1_description}
              </div>
            )}
            {limitations.phase2_description && (
              <div>
                <span className="text-slate-500">Phase 2 (Characteristics):</span> {limitations.phase2_description}
              </div>
            )}
            {limitations.additional_property_description && (
              <div>
                <span className="text-slate-500">Additional limitation:</span> {limitations.additional_property_description}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// 7. MetadataCard
interface MetadataCardProps {
  metadata: DatasetMetadata
}

export const MetadataCard: React.FC<MetadataCardProps> = ({ metadata }) => {
  return (
    <div className="border border-slate-800 bg-slate-900/30 rounded-lg p-4 flex flex-col gap-3 shadow-sm">
      <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider border-b border-slate-800 pb-1.5">
        Dataset & Observation Metadata
      </span>
      <div className="flex flex-col gap-2 text-xs text-slate-350">
        {metadata.library && (
          <div className="flex justify-between border-b border-slate-850/50 pb-1">
            <span className="text-slate-500 font-medium">Library/Methodology:</span>
            <span className="text-slate-300">{metadata.library}</span>
          </div>
        )}
        {metadata.source && (
          <div className="flex justify-between border-b border-slate-855 pb-1">
            <span className="text-slate-500 font-medium">Source Dataset:</span>
            <span className="text-slate-300">{metadata.source}</span>
          </div>
        )}
        {metadata.dataset_version && (
          <div className="flex justify-between border-b border-slate-855 pb-1">
            <span className="text-slate-500 font-medium">Dataset Version:</span>
            <span className="text-slate-300 font-mono">{metadata.dataset_version}</span>
          </div>
        )}
        {metadata.codes?.coverage !== undefined && metadata.codes?.coverage !== null && (
          <div className="flex justify-between border-b border-slate-855 pb-1">
            <span className="text-slate-500 font-medium">Coverage Code:</span>
            <span className="text-slate-300 font-mono">{metadata.codes.coverage}</span>
          </div>
        )}
        {metadata.reference_identifiers && metadata.reference_identifiers.length > 0 && (
          <div className="flex flex-col gap-1.5 pt-1.5">
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">Spatial Identifiers</span>
            <div className="grid grid-cols-2 gap-2 font-mono text-[11px] bg-slate-900/50 border border-slate-850 p-2 rounded">
              {metadata.reference_identifiers.map(([key, val], idx) => (
                <div key={idx} className="flex flex-col">
                  <span className="text-slate-500 text-[9px] uppercase font-sans">{key}</span>
                  <span className="text-teal-400 font-semibold">{val}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
