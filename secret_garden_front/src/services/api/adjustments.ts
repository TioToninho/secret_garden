import api from './axios'

export interface AdjustmentItem {
  id: number
  name: string
  start_date: string
  next_adjustment: string
  owner_id: number
  month: number
  year: number
}

export interface AdjustmentsResponse {
  data: {
    [key: string]: AdjustmentItem[]
  }
  error: string | null
}

export async function getNextAdjustments(): Promise<AdjustmentsResponse> {
  try {
    const response = await api.get<AdjustmentsResponse>('/api/clients/adjustments/next-3-months')
    return response.data
  } catch (error) {
    console.error('Erro ao buscar próximos ajustes:', error)
    throw error
  }
} 