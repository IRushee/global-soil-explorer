export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'

export interface Logger {
  debug(message: string, ...args: any[]): void
  info(message: string, ...args: any[]): void
  warn(message: string, ...args: any[]): void
  error(message: string, ...args: any[]): void
}

class ConsoleLogger implements Logger {
  private format(level: LogLevel, message: string): string {
    const timestamp = new Date().toISOString()
    return `[${timestamp}] [${level}]: ${message}`
  }

  debug(message: string, ...args: any[]): void {
    console.debug(this.format('DEBUG', message), ...args)
  }

  info(message: string, ...args: any[]): void {
    console.info(this.format('INFO', message), ...args)
  }

  warn(message: string, ...args: any[]): void {
    console.warn(this.format('WARNING', message), ...args)
  }

  error(message: string, ...args: any[]): void {
    console.error(this.format('ERROR', message), ...args)
  }
}

export const logger: Logger = new ConsoleLogger()
