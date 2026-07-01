# Application Event & Command Architecture

This document defines the decouple mechanisms that coordinate independent features in the Global Soil Explorer frontend: the **Application Event Bus** (reactive event architecture) and the **Command Pattern Engine** (transactional command architecture).

---

## 1. Application Event Bus (Event-Driven decoupled communication)

To prevent tight coupling between isolated modules (e.g. Map View, Sidebar, Search, Scientific Panel), the frontend uses a centralized typed Event Bus. Modules dispatch events without knowing who listens to them.

### A. Bus Interface Definition
```typescript
type AppEventType =
  | 'CoordinateSelected'
  | 'ObservationLoaded'
  | 'LayerChanged'
  | 'BasemapChanged'
  | 'DatasetChanged'
  | 'FilterChanged'
  | 'ExportRequested'
  | 'SearchCompleted'
  | 'StudyAreaChanged';

interface AppEvent<T = any> {
  type: AppEventType;
  payload: T;
  timestamp: number;
}

class AppEventBus {
  private listeners: Map<AppEventType, Set<(event: AppEvent) => void>> = new Map();

  subscribe<T>(type: AppEventType, callback: (event: AppEvent<T>) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(callback as any);
    
    // Return unsubscribe function
    return () => {
      this.listeners.get(type)?.delete(callback as any);
    };
  }

  dispatch<T>(type: AppEventType, payload: T): void {
    const event: AppEvent<T> = {
      type,
      payload,
      timestamp: Date.now(),
    };
    this.listeners.get(type)?.forEach(callback => callback(event));
  }
}

export const eventBus = new AppEventBus();
```

### B. Standard Events Definitions

| Event Name | Trigger Source | Primary Listener(s) | Payload Example |
| :--- | :--- | :--- | :--- |
| **`CoordinateSelected`** | Map click / coordinate input | Query Pipeline, Search panel | `{ lat: 52.0, lon: 10.0 }` |
| **`ObservationLoaded`** | Query Pipeline (success) | Info Panel, Vertical chart | `SoilObservation` (json object) |
| **`LayerChanged`** | Layer Manager sidebar | Map Renderer (re-sync) | `{ layerId: 'clay_share', visible: true, opacity: 0.8 }` |
| **`BasemapChanged`** | Basemap selector widget | Map Renderer (style switch) | `{ basemapId: 'dark-vector' }` |
| **`DatasetChanged`** | Global dataset dropdown | Map Renderer, Query pipeline | `{ datasetId: 'soilgrids' }` |
| **`FilterChanged`** | Range sliders / taxonomy input | Search sidebar, Query pipeline | `{ ph: [5.5, 7.0], clay: [10, 30] }` |
| **`ExportRequested`** | Info panel export action | Export Pipeline | `{ format: 'pdf', data: SoilObservation }` |
| **`SearchCompleted`** | Search autocomplete click | Map Renderer, Event Bus | `{ label: 'Rome, Italy', lat: 41.9, lon: 12.5 }` |
| **`StudyAreaChanged`** | Configuration init | Map Renderer (pan limits) | `{ bbox: [[-10, 35], [30, 70]] }` |

---

## 2. Command Architecture (User Transactions)

All state changes resulting from explicit user interactions are encapsulated in Command objects. This provides structural support for undo/redo history stacks, action recording, and macros.

### A. Command Pattern Contract
```typescript
interface Command {
  id: string;
  timestamp: number;
  execute(): void;
  undo(): void;
}

class CommandManager {
  private undoStack: Command[] = [];
  private redoStack: Command[] = [];
  private maxHistorySize: number = 50;

  executeCommand(command: Command): void {
    command.execute();
    this.undoStack.push(command);
    this.redoStack = []; // Clear redo stack on new command
    
    if (this.undoStack.length > this.maxHistorySize) {
      this.undoStack.shift();
    }
  }

  undo(): void {
    const command = this.undoStack.pop();
    if (command) {
      command.undo();
      this.redoStack.push(command);
    }
  }

  redo(): void {
    const command = this.redoStack.pop();
    if (command) {
      command.execute();
      this.undoStack.push(command);
    }
  }
}
```

### B. Standard Command Implementation Examples

#### 1. `SelectCoordinateCommand`
*   *Execute*: Updates active coordinate state pin, triggers pipeline fetch.
*   *Undo*: Reverts active coordinate state pin to the previous coordinate; clears panel displays if previous was None.

#### 2. `ToggleLayerCommand`
*   *Execute*: Changes layer visibility in the store and triggers event bus.
*   *Undo*: Restores previous layer visibility state.

#### 3. `SetFiltersCommand`
*   *Execute*: Appends range filter criteria to query state.
*   *Undo*: Reverts filter ranges to prior criteria bounds.
