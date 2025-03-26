import api from './axios'
import { ClientResponse, Client } from '@/types/client'

export const getClients = async (): Promise<ClientResponse> => {
  try {
    const response = await api.get<ClientResponse>('/api/clients/')
    return response.data
  } catch (error) {
    console.error('Erro ao buscar clientes:', error)
    throw error
  }
}

export const updateClient = async (id: number, data: Partial<Client>): Promise<Client> => {
  try {
    const response = await api.put<Client>(`/api/clients/${id}`, data)
    return response.data
  } catch (error) {
    console.error('Erro ao atualizar cliente:', error)
    throw error
  }
}

export const deleteClient = async (id: number): Promise<void> => {
  try {
    await api.delete(`/api/clients/${id}`)
  } catch (error) {
    console.error('Erro ao excluir cliente:', error)
    throw error
  }
}

export interface ClientNameResponse {
  data: ClientName[]
  error: null | string
}

export interface ClientName {
  id: number
  name: string
  owner_id: number
}

export async function getClientNames(): Promise<ClientNameResponse> {
  try {
    const response = await api.get<ClientNameResponse>('/api/clients/names')
    return response.data
  } catch (error) {
    console.error('Erro ao buscar nomes dos clientes:', error)
    throw error
  }
}

export interface ClientDetailResponse {
  data: ClientDetail
  error: null | string
}

export interface ClientDetail {
  id: number
  name: string
  status: string
  due_date: number
  amount_paid: number
  condo_fee: number
  percentage: number
  delivery_fee: number
  start_date: string
  condo_paid: boolean
  is_active: boolean
  owner_id: number
}

export async function getClientDetail(id: number): Promise<ClientDetailResponse> {
  try {
    const response = await api.get<ClientDetailResponse>(`/api/clients/${id}`)
    return response.data
  } catch (error) {
    console.error(`Erro ao buscar detalhes do cliente ${id}:`, error)
    throw error
  }
} 