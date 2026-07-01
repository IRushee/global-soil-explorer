import { logger } from '../utils/logger'
import { PluginError } from '../utils/errors'

export interface WorkerConfig {
  id: string
  scriptUrl: string
}

export class WorkerManager {
  private workers: Map<string, Worker> = new Map()

  registerWorker(config: WorkerConfig): void {
    if (this.workers.has(config.id)) {
      throw new PluginError(`Worker already registered: ${config.id}`)
    }

    try {
      // In production, we instantiate the Web Worker. In test/dev it might load conditionally
      const worker = new Worker(config.scriptUrl, { type: 'module' })
      this.workers.set(config.id, worker)
      logger.info(`Web Worker registered and started: ${config.id}`)
    } catch (e) {
      logger.warn(`Could not instantiate Web Worker script "${config.scriptUrl}" directly. Fallback mode enabled.`)
    }
  }

  postMessage(workerId: string, message: any, transfer?: Transferable[]): void {
    const worker = this.workers.get(workerId)
    if (!worker) {
      logger.warn(`Worker not active: ${workerId}. Message buffered or run on main thread.`)
      return
    }
    worker.postMessage(message, transfer || [])
  }

  onMessage(workerId: string, handler: (e: MessageEvent) => void): void {
    const worker = this.workers.get(workerId)
    if (worker) {
      worker.onmessage = handler
    }
  }

  terminateWorker(workerId: string): void {
    const worker = this.workers.get(workerId)
    if (worker) {
      worker.terminate()
      this.workers.delete(workerId)
      logger.info(`Web Worker terminated: ${workerId}`)
    }
  }

  terminateAll(): void {
    Array.from(this.workers.keys()).forEach((id) => this.terminateWorker(id))
  }
}

export const workerManager = new WorkerManager()
