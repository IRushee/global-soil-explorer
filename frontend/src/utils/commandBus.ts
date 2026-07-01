import { Command } from '../types'
import { logger } from './logger'

export class CommandManager {
  private undoStack: Command[] = []
  private redoStack: Command[] = []
  private readonly maxHistorySize: number = 50

  executeCommand(command: Command): void {
    logger.info(`Executing command: ${command.id}`)
    try {
      command.execute()
      this.undoStack.push(command)
      this.redoStack = [] // Clear redo stack on new action
      
      if (this.undoStack.length > this.maxHistorySize) {
        this.undoStack.shift()
      }
    } catch (err) {
      logger.error(`Failed to execute command ${command.id}:`, err)
      throw err
    }
  }

  undo(): void {
    const command = this.undoStack.pop()
    if (command) {
      logger.info(`Undoing command: ${command.id}`)
      try {
        command.undo()
        this.redoStack.push(command)
      } catch (err) {
        logger.error(`Failed to undo command ${command.id}:`, err)
        // Put it back to preserve stack integrity
        this.undoStack.push(command)
        throw err
      }
    } else {
      logger.warn('Undo stack empty')
    }
  }

  redo(): void {
    const command = this.redoStack.pop()
    if (command) {
      logger.info(`Redoing command: ${command.id}`)
      try {
        command.execute()
        this.undoStack.push(command)
      } catch (err) {
        logger.error(`Failed to redo command ${command.id}:`, err)
        this.redoStack.push(command)
        throw err
      }
    } else {
      logger.warn('Redo stack empty')
    }
  }

  getHistory(): { undoCount: number; redoCount: number } {
    return {
      undoCount: this.undoStack.length,
      redoCount: this.redoStack.length,
    }
  }

  clearHistory(): void {
    this.undoStack = []
    this.redoStack = []
    logger.info('Command history cleared')
  }
}

export const commandManager = new CommandManager()
