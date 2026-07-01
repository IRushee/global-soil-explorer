export class ApplicationError extends Error {
  constructor(message: string, public context?: Record<string, any>) {
    super(message)
    this.name = this.constructor.name
    Object.setPrototypeOf(this, new.target.prototype)
  }
}

export class DomainError extends ApplicationError {}
export class ValidationError extends ApplicationError {}
export class DatasetError extends ApplicationError {}
export class RepositoryError extends ApplicationError {}
export class PluginError extends ApplicationError {}
export class RendererError extends PluginError {}
export class ExportError extends PluginError {}

export class ConfigurationError extends ApplicationError {}
export class RouteError extends ApplicationError {}
export class MapError extends ApplicationError {}

export class AuthenticationError extends ApplicationError {}
export class AuthorizationError extends ApplicationError {}
