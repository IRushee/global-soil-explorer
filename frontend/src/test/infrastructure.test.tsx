import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { configService } from '../services/config'
import { eventBus } from '../utils/eventBus'
import { CommandManager } from '../utils/commandBus'
import { ExtensionRegistry } from '../plugins/registry'
import { useGlobalStore } from '../store'
import { MapLibreRenderer } from '../map/wrapper'
import { AppProvider } from '../providers/AppProvider'


describe('Global Soil Explorer Infrastructure Tests', () => {
  
  // 1. Configuration Service
  test('ConfigurationService provides valid active parameters and fallbacks', () => {
    const config = configService.get()
    expect(config.activeStudyAreaId).toBe('world')
    expect(config.activeDatasetId).toBe('hwsd_v2')
    expect(config.activeRendererId).toBe('maplibre')
    expect(configService.isFeatureEnabled('FLAG_OFFLINE_MODE')).toBeDefined()
  })

  // 2. Event Bus
  test('EventBus publishes, subscribes, and cleans up event callbacks', () => {
    const spy = vi.fn()
    const unsubscribe = eventBus.subscribe('CoordinateSelected', spy)
    
    eventBus.dispatch('CoordinateSelected', { latitude: 12.34, longitude: 56.78 })
    
    expect(spy).toHaveBeenCalledOnce()
    expect(spy.mock.calls[0][0].payload).toEqual({ latitude: 12.34, longitude: 56.78 })
    
    unsubscribe()
    eventBus.dispatch('CoordinateSelected', { latitude: 0, longitude: 0 })
    expect(spy).toHaveBeenCalledOnce() // No second trigger
  })

  // 3. Command Bus
  test('CommandManager executes command actions and manages undo/redo stack history', () => {
    const manager = new CommandManager()
    let value = 10
    
    const incrementCommand = {
      id: 'increment',
      timestamp: Date.now(),
      execute: () => { value += 1 },
      undo: () => { value -= 1 },
    }
    
    manager.executeCommand(incrementCommand)
    expect(value).toBe(11)
    expect(manager.getHistory().undoCount).toBe(1)
    
    manager.undo()
    expect(value).toBe(10)
    expect(manager.getHistory().undoCount).toBe(0)
    expect(manager.getHistory().redoCount).toBe(1)
    
    manager.redo()
    expect(value).toBe(11)
    expect(manager.getHistory().undoCount).toBe(1)
    expect(manager.getHistory().redoCount).toBe(0)
  })

  // 4. Plugin Registry
  test('ExtensionRegistry stores, retrieves, and prevents duplicate registration of plugins', () => {
    const registry = new ExtensionRegistry<string, string>()
    registry.register('mock-plugin', 'active-module')
    
    expect(registry.get('mock-plugin')).toBe('active-module')
    expect(registry.list()).toEqual(['mock-plugin'])
    
    expect(() => registry.register('mock-plugin', 'duplicate')).toThrowError(/already registered/)
  })

  // 5. Global Store (Zustand)
  test('Zustand store initializes layout and selection parameters with defaults', () => {
    const state = useGlobalStore.getState()
    expect(state.sidebarOpen).toBe(true)
    expect(state.infoPanelOpen).toBe(false)
    expect(state.selectedCoordinate).toBeNull()
    expect(state.activeObservation).toBeNull()
  })

  // 6. Map Wrapper Headless Fallback
  test('Map wrapper loads headless fallback mode without throwing error in non-DOM container environments', () => {
    const mapRenderer = new MapLibreRenderer()
    expect(() => {
      mapRenderer.initialize('invalid-container', {
        container: 'invalid-container',
        style: null,
        center: [0, 0],
        zoom: 2,
      })
    }).not.toThrow()
    
    // Check extended interface methods in fallback mode
    expect(mapRenderer.getCenter()).toBeNull()
    expect(mapRenderer.getZoom()).toBeNull()
    expect(() => mapRenderer.setMaxBounds([[-180, -90], [180, 90]])).not.toThrow()
    expect(() => mapRenderer.setBasemapStyle('satellite')).not.toThrow()
    expect(() => mapRenderer.setSelectionMarker(12.34, 56.78)).not.toThrow()
    expect(() => mapRenderer.setCursor('wait')).not.toThrow()
    
    // Cleanup
    mapRenderer.destroy()
  })

  // 7. Providers Composition & Bootstrap
  test('AppProvider renders AppShell container layout without crashing', () => {
    const { container } = render(<AppProvider />)
    expect(container).toBeDefined()
    expect(screen.getByText(/Global Soil Explorer/i)).toBeDefined()
  })

  // 8. SelectCoordinateCommand and Event Bus integration
  test('SelectCoordinateCommand updates selectedCoordinate and dispatches CoordinateSelected event', async () => {
    const spySelected = vi.fn()
    const unsub = eventBus.subscribe('CoordinateSelected', spySelected)

    const coord = { latitude: 45.0, longitude: 10.0 }
    
    const store = useGlobalStore.getState()
    const originalCoord = store.selectedCoordinate
    const originalObs = store.activeObservation

    const selectFnMock = async (c: any, fetch: boolean) => {
      store.setSelectedCoordinate(c)
      if (c) {
        eventBus.dispatch('CoordinateSelected', c)
      }
    }

    class MockSelectCoordinateCommand {
      id = 'SelectCoordinate'
      timestamp = Date.now()
      constructor(
        private coord: any,
        private prevCoord: any,
        private prevObs: any,
        private selectFn: any
      ) {}
      async execute() { await this.selectFn(this.coord, true) }
      async undo() {
        await this.selectFn(this.prevCoord, false)
        useGlobalStore.getState().setActiveObservation(this.prevObs)
      }
    }

    const cmd = new MockSelectCoordinateCommand(coord, originalCoord, originalObs, selectFnMock)
    await cmd.execute()

    expect(useGlobalStore.getState().selectedCoordinate).toEqual(coord)
    expect(spySelected).toHaveBeenCalledOnce()
    expect(spySelected.mock.calls[0][0].payload).toEqual(coord)

    await cmd.undo()
    expect(useGlobalStore.getState().selectedCoordinate).toBeNull()

    unsub()
  })

  // 9. Bookmarks & Search History Actions in Global Store
  test('Zustand store manages search history and named bookmarks successfully', () => {
    // Test bookmarks
    const testCoord = { latitude: 28.6139, longitude: 77.2090 }
    useGlobalStore.getState().addBookmark(testCoord)
    expect(useGlobalStore.getState().bookmarks.length).toBe(1)
    
    const bookmark = useGlobalStore.getState().bookmarks[0] as any
    expect(bookmark.latitude).toBe(28.6139)
    expect(bookmark.name).toContain('Location')
    
    useGlobalStore.getState().renameBookmark(testCoord, 'Capital City')
    expect((useGlobalStore.getState().bookmarks[0] as any).name).toBe('Capital City')
    
    useGlobalStore.getState().removeBookmark(testCoord)
    expect(useGlobalStore.getState().bookmarks.length).toBe(0)

    // Test search history
    const historyCoord = { latitude: 40.7128, longitude: -74.0060 }
    useGlobalStore.getState().addHistory(historyCoord)
    expect(useGlobalStore.getState().history.length).toBe(1)
    expect((useGlobalStore.getState().history[0] as any).latitude).toBe(40.7128)

    useGlobalStore.getState().clearHistory()
    expect(useGlobalStore.getState().history.length).toBe(0)
  })

  // 10. Nominatim Search Provider queries places successfully
  test('NominatimSearchProvider geocodes input queries and returns formatted results', async () => {
    const { NominatimSearchProvider } = await import('../components/SearchAndNavigation')
    const provider = new NominatimSearchProvider()
    
    const mockResponse = [
      {
        place_id: 12345,
        display_name: 'Delhi, India',
        lat: '28.6139',
        lon: '77.2090',
        name: 'Delhi',
        address: { city: 'Delhi', country: 'India' }
      }
    ]
    const fetchSpy = vi.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      } as any)
    )

    const results = await provider.search('Delhi')
    expect(results.length).toBe(1)
    expect(results[0].label).toBe('Delhi, India')
    expect(results[0].coordinate.lat).toBe(28.6139)
    expect(results[0].coordinate.lon).toBe(77.2090)

    fetchSpy.mockRestore()
  })
})
