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
    
    // Cleanup
    mapRenderer.destroy()
  })

  // 7. Providers Composition & Bootstrap
  test('AppProvider renders AppShell container layout without crashing', () => {
    const { container } = render(<AppProvider />)
    expect(container).toBeDefined()
    expect(screen.getByText(/Global Soil Explorer/i)).toBeDefined()
  })
})
