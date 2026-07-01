import { create } from 'zustand'
import { Coordinate, SoilObservation, StudyArea, OverlayLayer } from '../types'
import { configService } from '../services/config'
import { studyAreaRegistry } from '../services/studyArea'

// Slices State Interfaces
export interface ApplicationSlice {
  isInitialized: boolean
  setInitialized: (val: boolean) => void
}

export interface MapSlice {
  center: [number, number]
  zoom: number
  basemap: string
  overlays: OverlayLayer[]
  setCenter: (center: [number, number]) => void
  setZoom: (zoom: number) => void
  setBasemap: (basemap: string) => void
  setOverlays: (overlays: OverlayLayer[]) => void
}

export interface SelectionSlice {
  selectedCoordinate: Coordinate | null
  activeObservation: SoilObservation | null
  loading: boolean
  error: string | null
  activeProfileIndex: number
  activeLayerIndex: number | null
  setSelectedCoordinate: (coord: Coordinate | null) => void
  setActiveObservation: (obs: SoilObservation | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setActiveProfileIndex: (index: number) => void
  setActiveLayerIndex: (index: number | null) => void
}

export interface LayoutSlice {
  sidebarOpen: boolean
  infoPanelOpen: boolean
  activePanelTab: 'summary' | 'profiles' | 'charts' | 'export'
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setInfoPanelOpen: (open: boolean) => void
  setActivePanelTab: (tab: 'summary' | 'profiles' | 'charts' | 'export') => void
}

export interface ConfigurationSlice {
  activeStudyArea: StudyArea
  activeDatasetId: string
  activeRendererId: string
  setActiveStudyArea: (studyArea: StudyArea) => void
  setActiveDatasetId: (datasetId: string) => void
  setActiveRendererId: (rendererId: string) => void
}

export interface WorkspaceSlice {
  workspaceId: string
  bookmarks: Coordinate[]
  savedProjects: any[]
  history: Coordinate[]
  addBookmark: (coord: Coordinate) => void
  removeBookmark: (coord: Coordinate) => void
  addHistory: (coord: Coordinate) => void
}

export interface FeatureFlagsSlice {
  flags: Record<string, boolean>
  setFlag: (flag: string, enabled: boolean) => void
}

// Combined Global Store State
export type GlobalStoreState = ApplicationSlice &
  MapSlice &
  SelectionSlice &
  LayoutSlice &
  ConfigurationSlice &
  WorkspaceSlice &
  FeatureFlagsSlice

const defaultStudyArea = studyAreaRegistry.get('world')
const config = configService.get()

export const useGlobalStore = create<GlobalStoreState>((set) => ({
  // ApplicationSlice
  isInitialized: false,
  setInitialized: (val) => set({ isInitialized: val }),

  // MapSlice
  center: [worldStudyAreaCenterLongitude(defaultStudyArea), worldStudyAreaCenterLatitude(defaultStudyArea)],
  zoom: defaultStudyArea.defaultZoom,
  basemap: defaultStudyArea.availableBasemaps[0] || 'satellite',
  overlays: [],
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),
  setBasemap: (basemap) => set({ basemap }),
  setOverlays: (overlays) => set({ overlays }),

  // SelectionSlice
  selectedCoordinate: null,
  activeObservation: null,
  loading: false,
  error: null,
  activeProfileIndex: 0,
  activeLayerIndex: null,
  setSelectedCoordinate: (selectedCoordinate) => set({ selectedCoordinate }),
  setActiveObservation: (activeObservation) => set({ activeObservation }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setActiveProfileIndex: (activeProfileIndex) => set({ activeProfileIndex }),
  setActiveLayerIndex: (activeLayerIndex) => set({ activeLayerIndex }),

  // LayoutSlice
  sidebarOpen: true,
  infoPanelOpen: false,
  activePanelTab: 'summary',
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setInfoPanelOpen: (infoPanelOpen) => set({ infoPanelOpen }),
  setActivePanelTab: (activePanelTab) => set({ activePanelTab }),

  // ConfigurationSlice
  activeStudyArea: defaultStudyArea,
  activeDatasetId: config.activeDatasetId,
  activeRendererId: config.activeRendererId,
  setActiveStudyArea: (activeStudyArea) => set({ activeStudyArea }),
  setActiveDatasetId: (activeDatasetId) => set({ activeDatasetId }),
  setActiveRendererId: (activeRendererId) => set({ activeRendererId }),

  // WorkspaceSlice
  workspaceId: 'workspace_default',
  bookmarks: [],
  savedProjects: [],
  history: [],
  addBookmark: (coord) => set((state) => ({ bookmarks: [...state.bookmarks, coord] })),
  removeBookmark: (coord) =>
    set((state) => ({
      bookmarks: state.bookmarks.filter(
        (b) => b.latitude !== coord.latitude || b.longitude !== coord.longitude
      ),
    })),
  addHistory: (coord) => set((state) => ({ history: [coord, ...state.history].slice(0, 50) })),

  // FeatureFlagsSlice
  flags: { ...config.featureFlags },
  setFlag: (flag, enabled) =>
    set((state) => ({ flags: { ...state.flags, [flag]: enabled } })),
}))

// Helpers to extract coordinate centers safely
function worldStudyAreaCenterLongitude(area: StudyArea): number {
  return (area.bounds[0][0] + area.bounds[1][0]) / 2
}

function worldStudyAreaCenterLatitude(area: StudyArea): number {
  return (area.bounds[0][1] + area.bounds[1][1]) / 2
}
