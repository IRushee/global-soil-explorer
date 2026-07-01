import { AppEvent, AppEventType } from '../types'
import { logger } from './logger'

export class AppEventBus {
  private listeners: Map<AppEventType, Set<(event: AppEvent) => void>> = new Map()

  subscribe<T>(type: AppEventType, callback: (event: AppEvent<T>) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set())
    }
    this.listeners.get(type)!.add(callback as any)
    logger.debug(`Subscribed callback to event type: ${type}`)

    return () => {
      this.listeners.get(type)?.delete(callback as any)
      logger.debug(`Unsubscribed callback from event type: ${type}`)
    }
  }

  dispatch<T>(type: AppEventType, payload: T): void {
    const event: AppEvent<T> = {
      type,
      payload,
      timestamp: Date.now(),
    }
    logger.debug(`Dispatching event: ${type}`, payload)
    this.listeners.get(type)?.forEach((callback) => {
      try {
        callback(event)
      } catch (err) {
        logger.error(`Error in event listener for ${type}:`, err)
      }
    })
  }
}

export const eventBus = new AppEventBus()
