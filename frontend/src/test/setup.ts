import { beforeAll, vi } from 'vitest'

// Mock matchMedia for ThemeProvider checks
beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })

  // Mock Worker class for WorkerManager tests
  class MockWorker {
    url: string
    onmessage: ((e: MessageEvent) => void) | null = null
    constructor(url: string) {
      this.url = url
    }
    postMessage(message: any) {
      // Echo message back as async message event for testing
      setTimeout(() => {
        if (this.onmessage) {
          this.onmessage(new MessageEvent('message', { data: message }))
        }
      }, 0)
    }
    terminate() {}
  }

  Object.defineProperty(window, 'Worker', {
    value: MockWorker,
  })
})
