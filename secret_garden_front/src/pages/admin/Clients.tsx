import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getClientNames, deleteClient, ClientName } from '@/services/api/clients'
import { Table } from '@/components/common/Table'

const columns = [
  { 
    key: 'name' as keyof ClientName, 
    header: 'Nome',
    render: (client: ClientName) => (
      <button
        onClick={() => window.dispatchEvent(new CustomEvent('openClientDetail', { detail: client }))}
        className="text-primary-600 hover:text-primary-800"
      >
        {client.name}
      </button>
    )
  },
  {
    key: 'id' as keyof ClientName,
    header: 'Ações',
    render: (client: ClientName) => (
      <div className="flex space-x-2">
        <button
          onClick={() => window.dispatchEvent(new CustomEvent('editClient', { detail: client }))}
          className="text-gray-600 hover:text-gray-900"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          onClick={() => window.dispatchEvent(new CustomEvent('deleteClient', { detail: client }))}
          className="text-red-600 hover:text-red-900"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    )
  }
]

export function Clients() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['clientNames'],
    queryFn: getClientNames,
  })

  const deleteMutation = useMutation({
    mutationFn: deleteClient,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientNames'] })
    },
  })

  React.useEffect(() => {
    const handleOpenDetail = (event: CustomEvent) => {
      navigate(`/admin/clientes/${event.detail.id}`)
    }

    const handleEdit = (event: CustomEvent) => {
      navigate(`/admin/clientes/${event.detail.id}`)
    }

    const handleDelete = (event: CustomEvent) => {
      if (confirm('Tem certeza que deseja excluir este cliente?')) {
        deleteMutation.mutate(event.detail.id)
      }
    }

    window.addEventListener('openClientDetail', handleOpenDetail as EventListener)
    window.addEventListener('editClient', handleEdit as EventListener)
    window.addEventListener('deleteClient', handleDelete as EventListener)

    return () => {
      window.removeEventListener('openClientDetail', handleOpenDetail as EventListener)
      window.removeEventListener('editClient', handleEdit as EventListener)
      window.removeEventListener('deleteClient', handleDelete as EventListener)
    }
  }, [deleteMutation, navigate])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-600">
          Erro ao carregar os clientes. Por favor, tente novamente mais tarde.
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
        <button className="btn btn-primary">
          Novo Cliente
        </button>
      </div>
      <Table
        data={data?.data || []}
        columns={columns}
        className="shadow-sm"
      />
    </div>
  )
} 