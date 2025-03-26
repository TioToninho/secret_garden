import api from './axios'

export interface HealthCheckResponse {
  api: {
    status: string
    message: string
  }
  database: {
    status: string
    message: string
  }
  overall: string
}

export async function getHealthStatus(): Promise<HealthCheckResponse> {
  try {
    const response = await api.get<HealthCheckResponse>('/api/health/complete')
    return response.data
  } catch (error) {
    console.error('Erro ao verificar status do sistema:', error)
    throw error
  }
} 