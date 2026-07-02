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
  const metadata = observation.metadata
  const coverage = metadata?.coverage_description || 'Global Coverage'
  const version = metadata?.dataset_version || 'v2.0'
  const source = metadata?.source || 'HWSD'
  const library = metadata?.library
  const coverageCode = metadata?.codes?.coverage

  const formatLatitude = (lat: number) => {
    const suffix = lat >= 0 ? 'N' : 'S'
    return `${Math.abs(lat).toFixed(6)}° ${suffix}`
  }

  const formatLongitude = (lon: number) => {
    const suffix = lon >= 0 ? 'E' : 'W'
    return `${Math.abs(lon).toFixed(6)}° ${suffix}`
  }

  return (
    <div className="bg-theme-btn-bg/20 border border-theme-border p-4 rounded-2xl flex flex-col gap-3.5 shadow-sm hover-float">
      <div className="border-b border-theme-border pb-2">
        <h2 className="text-[10px] font-bold text-theme-text-muted uppercase tracking-wider block">Observation & Dataset Info</h2>
      </div>

      {/* Coordinates Row */}
      <div className="flex gap-4 items-center">
        <div className="flex-1">
          <span className="text-[10px] text-theme-text-muted font-medium uppercase tracking-wider block mb-0.5">Latitude</span>
          <span className="font-mono text-xs font-semibold text-theme-text">{formatLatitude(selectedCoordinate.latitude)}</span>
        </div>
        <div className="flex-1 border-l border-theme-border pl-4">
          <span className="text-[10px] text-theme-text-muted font-medium uppercase tracking-wider block mb-0.5">Longitude</span>
          <span className="font-mono text-xs font-semibold text-theme-text">{formatLongitude(selectedCoordinate.longitude)}</span>
        </div>
      </div>

      {/* Dataset Info List */}
      <div className="flex flex-col gap-1.5 text-xs pt-1.5 border-t border-theme-border">
        <div className="flex justify-between items-center py-0.5">
          <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Dataset</span>
          <span className="font-semibold text-theme-text uppercase">{datasetId.replace('_', ' ')} (v{version})</span>
        </div>
        {library && (
          <div className="flex justify-between items-center py-0.5">
            <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Methodology</span>
            <span className="font-medium text-theme-text">{library}</span>
          </div>
        )}
        <div className="flex justify-between items-center py-0.5">
          <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Source</span>
          <span className="font-medium text-theme-text italic">{source}</span>
        </div>
        <div className="flex justify-between items-center py-0.5">
          <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Profiles Found</span>
          <span className="font-semibold text-theme-text">{profileCount} {profileCount === 1 ? 'profile' : 'profiles'}</span>
        </div>
      </div>

      {/* Coverage & Spatial Identifiers Row */}
      <div className="grid grid-cols-2 gap-4 pt-2 border-t border-theme-border">
        <div className="flex flex-col gap-0.5">
          <span className="text-theme-text-muted text-[9px] uppercase font-bold tracking-wider block mb-0.5">Coverage</span>
          <p className="text-[11px] text-theme-text-sec leading-normal font-medium">
            {coverage} {coverageCode ? `(Code: ${coverageCode})` : ''}
          </p>
        </div>

        <div className="flex flex-col gap-1 border-l border-theme-border pl-4">
          <span className="text-[9px] text-theme-text-muted font-bold tracking-wider uppercase block mb-0.5">Spatial Identifiers</span>
          {metadata?.reference_identifiers && metadata.reference_identifiers.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {metadata.reference_identifiers.map(([key, val], idx) => (
                <div key={idx} className="px-1.5 py-0.5 bg-theme-btn-bg border border-theme-border rounded-lg text-[9px] font-mono flex gap-1 items-center select-all">
                  <span className="text-theme-text-muted text-[8px] uppercase font-sans font-semibold">{key}:</span>
                  <span className="text-teal-655 dark:text-teal-400 font-semibold">{val}</span>
                </div>
              ))}
            </div>
          ) : (
            <span className="text-[10px] text-theme-text-muted italic">None</span>
          )}
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
}export const ProfileSelector: React.FC<ProfileSelectorProps> = ({
  profiles,
  activeIndex,
  onChange,
}) => {
  if (!profiles || profiles.length <= 1) return null

  return (
    <div className="flex flex-col gap-2 font-sans">
      <h2 className="text-xs font-semibold text-theme-text-sec tracking-wide text-center">Mapping Unit Components:</h2>
      <div className="flex flex-wrap justify-center gap-2 p-1.5 rounded-2xl bg-theme-btn-bg/30 border border-theme-border">
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
              className={`text-[11px] px-3.5 py-1.5 rounded-xl transition-all duration-200 font-medium cursor-pointer shadow-xs ${
                isActive
                  ? 'bg-teal-500/10 text-teal-650 dark:text-teal-400 font-semibold border border-teal-500/20'
                  : 'bg-theme-card border border-theme-border text-theme-btn-text hover:text-theme-text hover:bg-theme-btn-bg/60'
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
  return (
    <div
      onClick={onClick}
      className={`border p-3 flex flex-col gap-1 transition-all duration-200 cursor-pointer select-none rounded-xl shadow-sm ${
        isActive
          ? 'bg-slate-900/45 border-l-2 border-l-teal-500 border-t-slate-800/40 border-r-slate-800/40 border-b-slate-800/40'
          : 'bg-slate-900/20 border-slate-800/40 hover:border-slate-700/40 hover:bg-slate-800/10'
      }`}
    >
      <div className="flex justify-between items-center text-xs">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono font-medium text-slate-500">Horizon #{index + 1}</span>
          <span className={`font-semibold ${isActive ? 'text-teal-400' : 'text-slate-200'}`}>
            {layer.top_depth_cm} - {layer.bottom_depth_cm} cm
          </span>
        </div>
        <span className="text-[10px] text-slate-500 font-mono font-light">
          {layer.bottom_depth_cm - layer.top_depth_cm} cm thick
        </span>
      </div>
    </div>
  )
}

// LayerList relocated below ScientificPropertyTable to allow embedding it.

// 5. ScientificPropertyTable
interface ScientificPropertyTableProps {
  layer: SoilLayer
}

export const PROPERTY_DEFINITIONS: Record<
  string,
  { label: string; definition: string; significance: string }
> = {
  sand: {
    label: 'Sand Fraction (0.05 - 2.0 mm)',
    definition: 'Coarse mineral particles. Sand creates large pores, allowing rapid water drainage and air circulation, but holds very little water or nutrients.',
    significance: 'High sand makes soil easy to till but dry and prone to nutrient leaching.',
  },
  silt: {
    label: 'Silt Fraction (0.002 - 0.05 mm)',
    definition: 'Medium-sized mineral particles that feel like flour. Silt holds moderate water and nutrients and is highly susceptible to water erosion.',
    significance: 'Silt provides good structure and moisture retention, but can compact easily, reducing air flow.',
  },
  clay: {
    label: 'Clay Fraction (< 0.002 mm)',
    definition: 'Microscopic mineral particles with vast surface areas and negative electrical charges that bind water and essential plant nutrients.',
    significance: 'High clay gives soil high nutrient and water capacity, but makes it sticky when wet and hard/cracked when dry, restricting root growth.',
  },
  bd: {
    label: 'Bulk Density',
    definition: 'The mass of dry soil divided by its total volume (including pore space).',
    significance: 'High bulk density (>1.6 g/cm³) indicates soil compaction, which restricts root growth, water movement, and oxygen availability.',
  },
  rbd: {
    label: 'Reference Bulk Density',
    definition: 'A standardized baseline bulk density for the soil type, used for comparison and to calculate stocks (e.g. soil carbon stocks).',
    significance: 'Used by researchers to evaluate compaction levels and estimate total nutrient weights per hectare.',
  },
  coarse: {
    label: 'Coarse Fragments',
    definition: 'Rock, gravel, and stones larger than 2 mm in diameter in the soil layer.',
    significance: 'High coarse fragments reduce the volume of active, fine soil. This limits the total amount of water and nutrients the soil can store.',
  },
  awc: {
    label: 'Available Water Capacity (AWC)',
    definition: 'The maximum amount of water a soil can store that is actually available for plants to absorb.',
    significance: 'High AWC acts as a buffer, allowing crops to survive longer periods without rain or irrigation.',
  },
  ph: {
    label: 'pH (H₂O)',
    definition: 'A measure of the acidity or alkalinity of the soil in water.',
    significance: 'Controls nutrient availability. Most crops prefer pH 6.0 to 7.5. Acidic soils (<5.5) can lock nutrients and cause aluminum toxicity; alkaline soils (>8.0) can lock phosphorus and iron.',
  },
  oc: {
    label: 'Organic Carbon',
    definition: 'The carbon contained within decomposed plant residues, animal waste, and soil microbes.',
    significance: 'The core indicator of soil fertility. It improves water holding, holds soil aggregates together, and feeds beneficial soil microbes.',
  },
  tn: {
    label: 'Total Nitrogen',
    definition: 'The sum of all nitrogen forms (organic and inorganic) present in the soil.',
    significance: 'A primary nutrient crucial for leaf growth, protein synthesis, and photosynthesis. Most nitrogen is stored in organic matter.',
  },
  cn: {
    label: 'C/N Ratio',
    definition: 'The ratio of organic carbon to nitrogen in the soil.',
    significance: 'Indicates how fast organic matter decomposes. A ratio of 10-12 is ideal. Ratios >20 slow down decomposition and temporarily lock up nitrogen; ratios <10 release nitrogen rapidly.',
  },
  cecSoil: {
    label: 'Cation Exchange Capacity (CEC) Soil',
    definition: 'A measure of how many positively charged nutrients (cations like Calcium, Magnesium, Potassium) the soil can hold and exchange.',
    significance: "The soil's 'nutrient reservoir'. Soils with high CEC can retain more nutrients and resist acidification.",
  },
  cecClay: {
    label: 'CEC Clay',
    definition: 'The cation exchange capacity specifically of the clay mineral portion of the soil.',
    significance: 'Helps identify clay mineral types. High CEC clays swell and shrink; low CEC clays are stable but less fertile.',
  },
  bs: {
    label: 'Base Saturation',
    definition: 'The percentage of the soil exchange complex occupied by basic nutrients (Ca, Mg, K, Na) instead of acidic ions (H, Al).',
    significance: 'High base saturation (>50%) indicates highly fertile, non-acidic soil with abundant nutrients for plants.',
  },
  ec: {
    label: 'Electrical Conductivity (EC)',
    definition: 'A measure of how easily electricity passes through a soil-water solution, reflecting salt content.',
    significance: 'Indicates salinity. High salinity (>2-4 dS/m) makes it hard for plant roots to draw water, reducing crop yields.',
  },
  caco3: {
    label: 'Calcium Carbonate (CaCO₃)',
    definition: 'The lime content of the soil.',
    significance: 'Helps neutralize acid. High CaCO₃ can keep pH alkaline (~8.2) and lock up key nutrients like phosphorus and iron.',
  },
  gypsum: {
    label: 'Gypsum (CaSO₄·2H₂O)',
    definition: 'A moderately soluble calcium sulfate mineral common in arid regions.',
    significance: 'Improves structure in sodic/compacted soils. However, extreme levels (>15%) can cause soil instability or sinkholes and limit roots.',
  },
}

export const ScientificPropertyTable: React.FC<ScientificPropertyTableProps> = ({ layer }) => {
  const [selectedProp, setSelectedProp] = React.useState<string | null>(null)

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

  const rows: {
    key: string
    label: string
    value: number | null
    unit: string
    formatter?: (v: number | null, u: string) => string
  }[] = [
    { key: 'bd', label: 'Bulk Density', value: bd.value, unit: bd.unit || 'g/cm³' },
    { key: 'rbd', label: 'Reference Bulk Density', value: rbd.value, unit: rbd.unit || 'g/cm³' },
    { key: 'coarse', label: 'Coarse Fragments', value: coarse.value, unit: coarse.unit || '%' },
    { key: 'awc', label: 'Available Water Capacity', value: awc.value, unit: awc.unit || '%' },
    { key: 'ph', label: 'pH (H₂O)', value: ph.value, unit: '', formatter: (v: number | null, _u: string) => v !== null ? v.toFixed(2) : 'N/A' },
    { key: 'oc', label: 'Organic Carbon', value: oc.value, unit: oc.unit || '%' },
    { key: 'tn', label: 'Total Nitrogen', value: tn.value, unit: tn.unit || '%' },
    { key: 'cn', label: 'C/N Ratio', value: cn.value, unit: cn.unit },
    { key: 'cecSoil', label: 'CEC Soil', value: cecSoil.value, unit: cecSoil.unit || 'cmol/kg' },
    { key: 'cecClay', label: 'CEC Clay', value: cecClay.value, unit: cecClay.unit || 'cmol/kg' },
    { key: 'bs', label: 'Base Saturation', value: bs.value, unit: bs.unit || '%' },
    { key: 'ec', label: 'Electrical Conductivity (EC)', value: ec.value, unit: ec.unit || 'dS/m' },
    { key: 'caco3', label: 'Calcium Carbonate', value: caco3.value, unit: caco3.unit || '%' },
    { key: 'gypsum', label: 'Gypsum', value: gypsum.value, unit: gypsum.unit || '%' },
  ]

  return (
    <div className="bg-theme-card border border-theme-border rounded-2xl p-4 flex flex-col gap-3 shadow-sm select-none hover-float">
      <h2 className="text-xs font-semibold text-theme-text uppercase tracking-wider border-b border-theme-border-sec pb-1.5 block">
        Horizon Measurements ({layer.top_depth_cm} - {layer.bottom_depth_cm} cm)
      </h2>

      {/* Texture Display */}
      {(sand.value !== null || silt.value !== null || clay.value !== null) && (
        <div className="flex flex-col gap-1.5 pb-2.5 border-b border-theme-border-sec">
          <div className="flex w-full h-1.5 rounded-full overflow-hidden bg-theme-btn-bg border border-theme-btn-border">
            {sand.value !== null && (
              <div style={{ width: `${sand.value}%` }} className="bg-amber-500/80 h-full" title={`Sand: ${sand.value}%`} />
            )}
            {silt.value !== null && (
              <div style={{ width: `${silt.value}%` }} className="bg-slate-400/80 h-full" title={`Silt: ${silt.value}%`} />
            )}
            {clay.value !== null && (
              <div style={{ width: `${clay.value}%` }} className="bg-red-500/80 h-full" title={`Clay: ${clay.value}%`} />
            )}
          </div>
          <div className="flex justify-between text-[10px] font-mono text-theme-text-muted">
            <span
              onClick={() => setSelectedProp(selectedProp === 'sand' ? null : 'sand')}
              className={`flex items-center gap-1.5 px-1.5 py-0.5 rounded-lg cursor-pointer hover:bg-theme-btn-bg/50 transition-colors ${
                selectedProp === 'sand' ? 'bg-amber-500/10 text-amber-500 font-semibold' : ''
              }`}
              title="Click to explain Sand"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500 inline-block"></span>
              Sand: {sand.value !== null ? `${sand.value.toFixed(1)}%` : 'N/A'}
            </span>
            <span
              onClick={() => setSelectedProp(selectedProp === 'silt' ? null : 'silt')}
              className={`flex items-center gap-1.5 px-1.5 py-0.5 rounded-lg cursor-pointer hover:bg-theme-btn-bg/50 transition-colors ${
                selectedProp === 'silt' ? 'bg-slate-400/10 text-slate-500 dark:text-slate-300 font-semibold' : ''
              }`}
              title="Click to explain Silt"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 inline-block"></span>
              Silt: {silt.value !== null ? `${silt.value.toFixed(1)}%` : 'N/A'}
            </span>
            <span
              onClick={() => setSelectedProp(selectedProp === 'clay' ? null : 'clay')}
              className={`flex items-center gap-1.5 px-1.5 py-0.5 rounded-lg cursor-pointer hover:bg-theme-btn-bg/50 transition-colors ${
                selectedProp === 'clay' ? 'bg-red-500/10 text-red-500 font-semibold' : ''
              }`}
              title="Click to explain Clay"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block"></span>
              Clay: {clay.value !== null ? `${clay.value.toFixed(1)}%` : 'N/A'}
            </span>
          </div>
        </div>
      )}

      {/* Tight single column parameters list */}
      <div className="flex flex-col gap-1 text-[11px] leading-relaxed">
        {rows.map((row) => {
          const isSelected = selectedProp === row.key
          return (
            <div
              key={row.key}
              onClick={() => setSelectedProp(isSelected ? null : row.key)}
              className={`flex justify-between cursor-pointer hover:bg-theme-btn-bg/50 px-1.5 py-0.5 rounded-lg transition-all ${
                isSelected
                  ? 'bg-teal-500/10 text-teal-650 dark:text-teal-400 font-semibold border-l-2 border-teal-500 pl-2'
                  : 'text-theme-text-sec'
              }`}
              title={`Click to explain ${row.label}`}
            >
              <span className={isSelected ? 'text-teal-650 dark:text-teal-400 font-semibold' : 'text-theme-text-muted font-light'}>
                {row.label}:
              </span>
              <span className="font-mono text-theme-text">
                {row.formatter ? row.formatter(row.value, row.unit) : formatVal(row.value, row.unit)}
              </span>
            </div>
          )
        })}
      </div>

      {/* Interactive Glossary Detail Card */}
      {selectedProp && PROPERTY_DEFINITIONS[selectedProp] ? (
        <div className="mt-2 p-3.5 bg-teal-50/50 dark:bg-teal-955/15 backdrop-blur-sm border-l-2 border-l-teal-500 rounded-r-xl text-xs leading-relaxed transition-all duration-200 shadow-md">
          <div className="flex justify-between items-center mb-1 border-b border-teal-900/20 pb-0.5">
            <span className="font-bold text-teal-600 dark:text-teal-400 text-[11px] tracking-wide">
              {PROPERTY_DEFINITIONS[selectedProp].label}
            </span>
            <button
              onClick={() => setSelectedProp(null)}
              className="text-[10px] text-theme-text-muted hover:text-theme-text cursor-pointer"
            >
              Close
            </button>
          </div>
          <p className="text-theme-text-sec font-normal mb-1.5 leading-normal">
            {PROPERTY_DEFINITIONS[selectedProp].definition}
          </p>
          <div className="text-theme-text-muted text-[11px] leading-normal">
            <span className="text-teal-600 dark:text-teal-500/70 font-bold tracking-wider text-[9px] uppercase mr-1 inline-block">
              Significance:
            </span>
            {PROPERTY_DEFINITIONS[selectedProp].significance}
          </div>
        </div>
      ) : (
        <div className="mt-0.5 text-center text-[10px] text-theme-text-muted italic select-none">
          💡 Tip: Click any row or texture label to view its scientific explanation.
        </div>
      )}
    </div>
  )
}

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
    return <div className="text-xs text-theme-text-muted italic">No depth layers available.</div>
  }

  const selectedLayer = activeLayerIndex !== null ? layers[activeLayerIndex] : null

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h2 className="text-xs font-semibold text-theme-text-sec tracking-wide">Select Depth Layer</h2>
        <div className="grid grid-cols-4 gap-1.5">
          {layers.map((layer: SoilLayer, idx: number) => {
            const isActive = idx === activeLayerIndex
            return (
              <button
                key={idx}
                onClick={() => onLayerSelect(isActive ? null : idx)}
                className={`py-2 px-1 rounded-xl text-center border text-[11px] font-medium transition-all duration-200 cursor-pointer select-none ${
                  isActive
                    ? 'bg-teal-500/10 border-teal-500 text-teal-600 dark:text-teal-400 font-semibold shadow-sm'
                    : 'bg-theme-btn-bg border-theme-btn-border text-theme-btn-text hover:text-theme-text hover:bg-theme-btn-bg/80'
                }`}
              >
                <div className="text-[9px] text-theme-text-muted font-mono leading-none mb-0.5">#{idx + 1}</div>
                <div className="font-semibold leading-none text-[10px]">{layer.top_depth_cm}-{layer.bottom_depth_cm}</div>
              </button>
            )
          })}
        </div>
      </div>

      {selectedLayer ? (
        <div className="transition-all duration-300 ease-in-out">
          <ScientificPropertyTable layer={selectedLayer} />
        </div>
      ) : (
        <div className="text-center py-6 border border-dashed border-theme-border rounded-2xl text-[11px] text-theme-text-muted italic bg-theme-card select-none">
          👆 Select a depth layer button above to view scientific measurements.
        </div>
      )}
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
    <div className="bg-theme-card border border-theme-border rounded-2xl p-4 flex flex-col gap-3 shadow-sm select-none hover-float">
      <h2 className="text-xs font-semibold text-theme-text uppercase tracking-wider border-b border-theme-border-sec pb-1.5 block">
        Soil Classification & Context
      </h2>

      {/* Taxonomy Section */}
      <div className="flex flex-col gap-3">
        {/* Main Taxonomic Name and Symbol Code with prominent emphasis */}
        <div className="flex items-start justify-between gap-3 pb-2 border-b border-theme-border-sec">
          <div className="flex flex-col gap-0.5">
            <span className="text-[10px] text-theme-text-muted font-semibold uppercase tracking-wider">Taxonomic Name</span>
            <div className="text-theme-text font-bold text-sm select-all">{classification.class_name}</div>
          </div>
          {classification.codes.class_symbol && (
            <div className="flex flex-col items-end gap-0.5">
              <span className="text-[10px] text-theme-text-muted font-semibold uppercase tracking-wider">Symbol</span>
              <span className="px-2.5 py-0.5 bg-teal-500/10 text-teal-650 dark:text-teal-400 font-mono font-bold text-xs rounded-lg border border-teal-500/20">{classification.codes.class_symbol}</span>
            </div>
          )}
        </div>

        {/* Sub-standards Justified list */}
        <div className="flex flex-col gap-1.5 text-xs">
          {classification.taxonomy_standard && (
            <div className="flex justify-between items-center py-0.5">
              <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Standard</span>
              <span className="font-medium text-theme-text text-right">{classification.taxonomy_standard}</span>
            </div>
          )}
          {classification.wrb4_name && (
            <div className="flex justify-between items-center py-0.5">
              <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">WRB 2022 (4th Ed)</span>
              <span className="font-medium text-theme-text text-right">{classification.wrb4_name}</span>
            </div>
          )}
          {classification.wrb2_name && (
            <div className="flex justify-between items-center py-0.5">
              <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">WRB 2006 (2nd Ed)</span>
              <span className="font-medium text-theme-text text-right">{classification.wrb2_name}</span>
            </div>
          )}
          {classification.fao90_name && (
            <div className="flex justify-between items-center py-0.5">
              <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">FAO 1990</span>
              <span className="font-medium text-theme-text text-right">{classification.fao90_name}</span>
            </div>
          )}
          {classification.wrb_phase_name && (
            <div className="flex justify-between items-center py-0.5">
              <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">WRB Phase</span>
              <span className="font-medium text-theme-text text-right">{classification.wrb_phase_name}</span>
            </div>
          )}
        </div>
      </div>

      {/* Hydrology Section */}
      {hydro && (
        <div className="flex flex-col gap-1.5 pt-2.5 border-t border-theme-border-sec">
          <h3 className="text-[10px] text-theme-text-muted font-semibold uppercase tracking-wider mb-0.5">Hydrologic Context</h3>
          <div className="flex flex-col gap-1.5 text-xs">
            {hydro.drainage_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Drainage Class</span>
                <span className="font-medium text-theme-text text-right">{hydro.drainage_description}</span>
              </div>
            )}
            {hydro.water_regime_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Water Regime</span>
                <span className="font-medium text-theme-text text-right">{hydro.water_regime_description}</span>
              </div>
            )}
            {hydro.impermeable_layer_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Impermeable Horizon</span>
                <span className="font-medium text-theme-text text-right">{hydro.impermeable_layer_description}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Land Limitations Section */}
      {limitations && (
        <div className="flex flex-col gap-1.5 pt-2.5 border-t border-theme-border-sec">
          <h3 className="text-[10px] text-theme-text-muted font-semibold uppercase tracking-wider mb-0.5">Limiting Factors</h3>
          <div className="flex flex-col gap-1.5 text-xs">
            {limitations.root_depth_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Root Depth Limit</span>
                <span className="font-medium text-theme-text text-right">{limitations.root_depth_description}</span>
              </div>
            )}
            {limitations.root_obstacles_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Root Obstacles</span>
                <span className="font-medium text-theme-text text-right">{limitations.root_obstacles_description}</span>
              </div>
            )}
            {limitations.phase1_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Phase 1</span>
                <span className="font-medium text-theme-text text-right">{limitations.phase1_description}</span>
              </div>
            )}
            {limitations.phase2_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Phase 2</span>
                <span className="font-medium text-theme-text text-right">{limitations.phase2_description}</span>
              </div>
            )}
            {limitations.additional_property_description && (
              <div className="flex justify-between items-center py-0.5">
                <span className="text-theme-text-muted text-[10px] uppercase font-medium tracking-wider">Additional limitation</span>
                <span className="font-medium text-theme-text text-right">{limitations.additional_property_description}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}


