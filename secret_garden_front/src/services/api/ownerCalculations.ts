import api from './axios'
import { MonthlyCalculation } from './monthlyCalculations'

export interface OwnerMonthlyCalculationsResponse {
  data: MonthlyCalculation[]
}

export const getOwnerMonthlyCalculations = async (
  ownerId: number,
  month: number,
  year: number
): Promise<OwnerMonthlyCalculationsResponse> => {
  try {
    const response = await api.get(
      `/api/monthly-calculations/owner/${ownerId}?month=${month}&year=${year}`
    )
    return response.data
  } catch (error) {
    console.error(`Erro ao buscar cálculos mensais para o proprietário ${ownerId}:`, error)
    throw error
  }
} 