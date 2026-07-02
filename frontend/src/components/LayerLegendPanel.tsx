import React, { useState } from 'react'
import { Eye, EyeOff, Sliders, Info, ChevronDown, ChevronRight, ArrowUp, ArrowDown } from 'lucide-react'
import { useGlobalStore } from '../store'
import { OverlayLayer } from '../types'
import { mapRenderer } from '../map/wrapper'
import { logger } from '../utils/logger'

const CATEGORIES = [
  { id: 'physical', name: 'Physical Soil Layers', layerIds: ['hwsd_texture', 'hwsd_bd', 'hwsd_coarse'] },
  { id: 'chemical', name: 'Chemical Soil Layers', layerIds: ['hwsd_ph', 'hwsd_oc', 'hwsd_cec', 'hwsd_bs'] },
  { id: 'taxonomy', name: 'Hydrology & Taxonomy', layerIds: ['hwsd_drainage', 'hwsd_wrb'] }
]

export const LayerLegendPanel: React.FC = () => {
  const { overlays, setOverlays } = useGlobalStore()
  const [activeLayerId, setActiveLayerId] = useState<string | null>('hwsd_texture')
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    physical: true,
    chemical: true,
    taxonomy: true
  })
  const [expandedMetadata, setExpandedMetadata] = useState<Record<string, boolean>>({})

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => ({ ...prev, [groupId]: !prev[groupId] }))
  }

  const toggleMetadata = (layerId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setExpandedMetadata(prev => ({ ...prev, [layerId]: !prev[layerId] }))
  }

  const toggleLayerVisibility = (layerId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const updated = overlays.map(layer => {
      if (layer.id === layerId) {
        const nextVisible = !layer.visible
        // Sync directly to the map renderer instance
        try {
          mapRenderer.updateLayer(layerId, { visible: nextVisible })
        } catch (err) {
          logger.warn('Failed to update layer visibility in renderer:', err)
        }
        return { ...layer, visible: nextVisible }
      }
      return layer
    })
    setOverlays(updated)
  }

  const changeLayerOpacity = (layerId: string, opacity: number) => {
    const updated = overlays.map(layer => {
      if (layer.id === layerId) {
        const targetOpacity = opacity / 100
        // Sync directly to map renderer instance
        try {
          mapRenderer.updateLayer(layerId, { opacity: targetOpacity })
        } catch (err) {
          logger.warn('Failed to update layer opacity in renderer:', err)
        }
        return { ...layer, opacity: targetOpacity }
      }
      return layer
    })
    setOverlays(updated)
  }

  const moveLayerOrder = (layerId: string, direction: 'up' | 'down', e: React.MouseEvent) => {
    e.stopPropagation()
    const index = overlays.findIndex(l => l.id === layerId)
    if (index === -1) return

    const nextIndex = direction === 'up' ? index - 1 : index + 1
    if (nextIndex < 0 || nextIndex >= overlays.length) return

    const updated = [...overlays]
    const temp = updated[index]
    updated[index] = updated[nextIndex]
    updated[nextIndex] = temp
    setOverlays(updated)
  }

  const batchToggleGroup = (layerIds: string[], targetVisible: boolean, e: React.MouseEvent) => {
    e.stopPropagation()
    const updated = overlays.map(layer => {
      if (layerIds.includes(layer.id)) {
        try {
          mapRenderer.updateLayer(layer.id, { visible: targetVisible })
        } catch (err) {
          logger.warn('Failed to update layer visibility in renderer:', err)
        }
        return { ...layer, visible: targetVisible }
      }
      return layer
    })
    setOverlays(updated)
  }

  return (
    <div className="flex flex-col gap-3 select-none">
      <h3 className="text-[10px] font-bold text-theme-text-muted uppercase tracking-wider mb-0.5">
        Thematic Overlays & Legends
      </h3>
      <div className="flex flex-col gap-2.5">
        {CATEGORIES.map(category => {
          const catLayers = overlays.filter(l => category.layerIds.includes(l.id))
          const isExpanded = expandedGroups[category.id]

          return (
            <div key={category.id} className="flex flex-col gap-2">
              {/* Category Header */}
              <div
                onClick={() => toggleGroup(category.id)}
                className="flex items-center justify-between cursor-pointer py-1 border-b border-theme-border-sec hover:text-theme-text transition-colors text-theme-text-sec"
              >
                <div className="flex items-center gap-1.5">
                  {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                  <h3 className="text-[10px] font-bold uppercase tracking-wider">
                    {category.name}
                  </h3>
                </div>

                {/* Batch toggles */}
                <div className="flex items-center gap-2 text-[9px] font-medium">
                  <button
                    onClick={(e) => batchToggleGroup(category.layerIds, true, e)}
                    className="hover:text-teal-650 dark:hover:text-teal-400 cursor-pointer"
                  >
                    Enable All
                  </button>
                  <span className="text-theme-border">|</span>
                  <button
                    onClick={(e) => batchToggleGroup(category.layerIds, false, e)}
                    className="hover:text-teal-650 dark:hover:text-teal-400 cursor-pointer"
                  >
                    Disable All
                  </button>
                </div>
              </div>

              {/* Group Layers */}
              {isExpanded && (
                <div className="flex flex-col gap-2.5 pl-1.5">
                  {catLayers.map((layer) => {
                    const isSelected = activeLayerId === layer.id
                    const isMetaExpanded = !!expandedMetadata[layer.id]
                    const rawIdx = overlays.findIndex(l => l.id === layer.id)
                    const canMoveUp = rawIdx > 0
                    const canMoveDown = rawIdx < overlays.length - 1

                    return (
                      <div
                        key={layer.id}
                        onClick={() => setActiveLayerId(layer.id)}
                        className={`border rounded-2xl p-3 hover-float bg-theme-card flex flex-col gap-2.5 transition-all duration-200 shadow-xs cursor-pointer ${
                          isSelected
                            ? 'border-teal-500 ring-1 ring-teal-500/10'
                            : 'border-theme-border hover:border-theme-border/80'
                        }`}
                      >
                        {/* Title Bar */}
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                            <div className="flex items-center gap-1.5 min-w-0">
                              <span className={`text-xs font-semibold truncate leading-tight ${isSelected ? 'text-teal-650 dark:text-teal-400' : 'text-theme-text-sec'}`}>
                                {layer.title}
                              </span>
                              {isSelected && (
                                <span className="text-[8px] font-bold px-1.5 py-0.2 bg-teal-500/10 text-teal-650 dark:text-teal-400 border border-teal-500/20 rounded-md">
                                  ACTIVE
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-theme-text-muted leading-tight truncate">
                              {layer.description}
                            </span>
                          </div>

                          {/* Controls Row */}
                          <div className="flex items-center gap-1.5">
                            {/* Move Up */}
                            <button
                              disabled={!canMoveUp}
                              onClick={(e) => moveLayerOrder(layer.id, 'up', e)}
                              className={`p-1 rounded-md border transition-all cursor-pointer ${
                                canMoveUp
                                  ? 'bg-theme-btn-bg border-theme-btn-border text-theme-text hover:text-teal-500'
                                  : 'opacity-30 cursor-not-allowed text-theme-text-muted'
                              }`}
                              title="Move Layer Up"
                            >
                              <ArrowUp className="w-3 h-3" />
                            </button>

                            {/* Move Down */}
                            <button
                              disabled={!canMoveDown}
                              onClick={(e) => moveLayerOrder(layer.id, 'down', e)}
                              className={`p-1 rounded-md border transition-all cursor-pointer ${
                                canMoveDown
                                  ? 'bg-theme-btn-bg border-theme-btn-border text-theme-text hover:text-teal-500'
                                  : 'opacity-30 cursor-not-allowed text-theme-text-muted'
                              }`}
                              title="Move Layer Down"
                            >
                              <ArrowDown className="w-3 h-3" />
                            </button>

                            {/* Metadata Info */}
                            <button
                              onClick={(e) => toggleMetadata(layer.id, e)}
                              className={`p-1 rounded-md border transition-all cursor-pointer ${
                                isMetaExpanded
                                  ? 'bg-teal-500/10 border-teal-500/20 text-teal-655 dark:text-teal-400'
                                  : 'bg-theme-btn-bg border-theme-btn-border text-theme-text-muted hover:text-theme-text'
                              }`}
                              title="Show Layer Metadata"
                            >
                              <Info className="w-3 h-3" />
                            </button>

                            {/* Visibility Eye */}
                            <button
                              onClick={(e) => toggleLayerVisibility(layer.id, e)}
                              className={`p-1.5 rounded-lg border transition-all duration-200 cursor-pointer ${
                                layer.visible
                                  ? 'bg-teal-500/10 border-teal-500/20 text-teal-650 dark:text-teal-400'
                                  : 'bg-theme-btn-bg border-theme-btn-border text-theme-text-muted hover:text-theme-text'
                              }`}
                              title={layer.visible ? 'Hide Layer' : 'Show Layer'}
                            >
                              {layer.visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                            </button>
                          </div>
                        </div>

                        {/* Metadata Expanded Card */}
                        {isMetaExpanded && (
                          <div className="text-[9px] p-2 bg-theme-btn-bg/20 border border-theme-border-sec rounded-xl flex flex-col gap-1 text-theme-text-sec animate-fade-in font-sans">
                            <div className="flex justify-between"><span className="text-theme-text-muted">Dataset:</span> <span className="font-medium">{layer.dataset}</span></div>
                            <div className="flex justify-between"><span className="text-theme-text-muted">Type:</span> <span className="font-mono">{layer.type.toUpperCase()} ({layer.renderer})</span></div>
                            <div className="flex justify-between"><span className="text-theme-text-muted">Resolution:</span> <span>30 arc-seconds (~1km)</span></div>
                            <div className="flex justify-between"><span className="text-theme-text-muted">Coverage:</span> <span>Global (study areas)</span></div>
                            <div className="flex justify-between"><span className="text-theme-text-muted">Attribution:</span> <span className="italic text-right">FAO / IIASA / ISRIC</span></div>
                            <div className="flex justify-between"><span className="text-theme-text-muted">Last Updated:</span> <span>2024</span></div>
                          </div>
                        )}

                        {/* Opacity and Legends (Expanded if visible or active) */}
                        {layer.visible && (
                          <div className="flex flex-col gap-2.5 pt-2 border-t border-theme-border-sec animate-fade-in">
                            {/* Opacity Control */}
                            <div className="flex items-center justify-between gap-3 text-[10px] text-theme-text-sec">
                              <div className="flex items-center gap-1 text-[9px] font-medium text-theme-text-muted uppercase tracking-wider">
                                <Sliders className="w-3 h-3" />
                                <span>Opacity: {Math.round(layer.opacity * 100)}%</span>
                              </div>
                              <input
                                type="range"
                                min="0"
                                max="100"
                                value={Math.round(layer.opacity * 100)}
                                onChange={(e) => changeLayerOpacity(layer.id, parseInt(e.target.value))}
                                className="w-24 h-1 bg-theme-btn-bg rounded-lg appearance-none cursor-pointer accent-teal-500"
                              />
                            </div>

                            {/* Legend Display */}
                            {layer.legend && (
                              <div className="flex flex-col gap-1 mt-0.5">
                                <div className="text-[9px] font-bold text-theme-text-sec flex justify-between">
                                  <span>{layer.legend.title}</span>
                                  {layer.legend.unit && <span className="text-theme-text-muted font-normal">({layer.legend.unit})</span>}
                                </div>
                                <div
                                  style={{
                                    background: `linear-gradient(to right, ${layer.legend.colors.join(', ')})`
                                  }}
                                  className="h-1.5 w-full rounded-full border border-black/5 dark:border-white/5"
                                />
                                <div className="flex justify-between text-[9px] font-mono text-theme-text-muted">
                                  {layer.legend.labels.map((label: string, idx: number) => (
                                    <span key={idx}>{label}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
