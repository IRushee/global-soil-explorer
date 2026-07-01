import axios, { AxiosError, AxiosInstance } from 'axios'
import { Coordinate, SoilObservation } from '../types'
import { configService } from '../services/config'
import { ValidationError, RepositoryError } from '../utils/errors'
import { logger } from '../utils/logger'

const config = configService.get()

export const apiClient: AxiosInstance = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// Request Interceptor
apiClient.interceptors.request.use(
  (request) => {
    logger.debug(`HTTP Request: [${request.method?.toUpperCase()}] ${request.url}`)
    return request
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response Interceptor with error normalization
apiClient.interceptors.response.use(
  (response) => {
    logger.debug(`HTTP Response: ${response.status} for ${response.config.url}`)
    return response
  },
  (error: AxiosError<any>) => {
    const status = error.response?.status
    const message = error.response?.data?.detail || error.message || 'Unknown network error'

    logger.error(`HTTP Error: ${status || 'No Status'} - ${message}`)

    if (status === 400) {
      return Promise.reject(new ValidationError(message, { status, data: error.response?.data }))
    }

    return Promise.reject(new RepositoryError(`Backend server error: ${message}`, { status }))
  }
)

// Typed API Layer (Basic structure placeholders)
export const soilApi = {
  async getSoilObservation(coords: Coordinate): Promise<SoilObservation | null> {
    try {
      const response = await apiClient.get<SoilObservation>('/soil', {
        params: {
          latitude: coords.latitude,
          longitude: coords.longitude,
        },
      })
      if (response.status === 204 || !response.data) {
        return null
      }
      return response.data
    } catch (e) {
      logger.error('Failed to get soil observation:', e)
      throw e
    }
  },

  async getHealth(): Promise<{ status: string }> {
    try {
      const response = await apiClient.get<{ status: string }>('/health')
      return response.data
    } catch (e) {
      logger.error('Failed health check:', e)
      throw e
    }
  },
}
