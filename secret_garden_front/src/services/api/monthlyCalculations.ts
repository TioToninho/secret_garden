import api from './axios'

export interface MonthlyCalculation {
  id: number
  client_id: number
  month: number
  year: number
  rent_amount: number
  calculation_base: number
  tenant_payment: number
  commission: number
  deposit_amount: number
  created_at: string
  updated_at: string | null
}

export interface MonthlyCalculationsResponse {
  data: MonthlyCalculation[]
  error: null | string
}

export async function getClientMonthlyCalculations(
  clientId: number
): Promise<MonthlyCalculationsResponse> {
  try {
    const response = await api.get<MonthlyCalculationsResponse>(
      `/api/monthly-calculations/client/${clientId}`
    )
    return response.data
  } catch (error) {
    console.error(`Erro ao buscar cálculos mensais para o cliente ${clientId}:`, error)
    throw error
  }
} 