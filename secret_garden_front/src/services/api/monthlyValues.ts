import api from './axios'

export interface PendingMonthlyValue {
  id: number
  client_id: number
  client_name: string
  month: number
  year: number
  water_bill: number | null
  gas_bill: number | null
  insurance: number | null
  property_tax: number | null
  condo_fee: number | null
  updated_at: string
}

export interface PendingMonthlyValuesResponse {
  data: PendingMonthlyValue[]
}

export interface MonthlyVariableValue {
  id: number
  client_id: number
  month: number
  year: number
  water_bill: number | null
  gas_bill: number | null
  insurance: number | null
  property_tax: number | null
  condo_fee: number | null
  created_at: string
  updated_at: string
}

export interface MonthlyVariableValuesResponse {
  data: MonthlyVariableValue[]
}

export interface MonthlyVariableValueUpdate {
  water_bill?: number
  gas_bill?: number
  insurance?: number
  property_tax?: number
  condo_fee?: number
  [key: string]: number | undefined
}

export const getPendingMonthlyValues = async (): Promise<PendingMonthlyValuesResponse> => {
  try {
    const response = await api.get('/api/monthly-variable-values/pending')
    return response.data
  } catch (error) {
    console.error('Error fetching pending monthly values:', error)
    throw error
  }
}

export const getClientMonthlyVariableValues = async (clientId: number): Promise<MonthlyVariableValuesResponse> => {
  try {
    const response = await api.get(`/api/monthly-variable-values/client/${clientId}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching monthly variable values for client ${clientId}:`, error)
    throw error
  }
}

export const updateMonthlyValues = async (
  clientId: number,
  month: number,
  year: number,
  data: Partial<MonthlyVariableValue>
): Promise<void> => {
  try {
    await api.put(`/api/monthly-variable-values/${clientId}/${month}/${year}`, data)
  } catch (error) {
    console.error('Error updating monthly values:', error)
    throw error
  }
} 