import api from './axios'

export interface OwnerResponse {
  data: Owner[]
  error: string | null
}

export interface Owner {
  id: number
  name: string
  created_at: string
  updated_at: string | null
}

export async function getOwners(): Promise<OwnerResponse> {
  try {
    const response = await api.get<OwnerResponse>('/api/owners/')
    return response.data
  } catch (error) {
    console.error('Erro ao buscar proprietários:', error)
    throw error
  }
}

export async function updateOwner(id: number, data: Partial<Owner>): Promise<Owner> {
  const response = await api.put<Owner>(`/api/owners/${id}`, data)
  return response.data
}

export async function deleteOwner(id: number): Promise<void> {
  await api.delete(`/api/owners/${id}`)
}

export async function createOwner(data: Partial<Owner>): Promise<Owner> {
  const response = await api.post<Owner>('/api/owners/', data)
  return response.data
} 