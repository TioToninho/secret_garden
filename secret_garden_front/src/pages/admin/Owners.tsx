import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getOwners, updateOwner, deleteOwner } from '@/services/api/owners'
import { Table } from '@/components/common/Table'
import { Modal } from '@/components/common/Modal'
import { Owner } from '@/services/api/owners'
import { useNavigate } from 'react-router-dom'

const columns = [
  { 
    key: 'name' as keyof Owner, 
    header: 'Nome',
    render: (owner: Owner) => (
      <button
        onClick={() => window.dispatchEvent(new CustomEvent('openOwnerDetails', { detail: owner }))}
        className="text-primary-600 hover:text-primary-800"
      >
        {owner.name}
      </button>
    )
  },
  {
    key: 'id' as keyof Owner,
    header: 'Ações',
    render: (owner: Owner) => (
      <div className="flex space-x-2">
        <button
          onClick={() => window.dispatchEvent(new CustomEvent('openOwnerEdit', { detail: owner }))}
          className="text-gray-600 hover:text-gray-900"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          onClick={() => window.dispatchEvent(new CustomEvent('deleteOwner', { detail: owner }))}
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

export function Owners() {
  const [selectedOwner, setSelectedOwner] = useState<Owner | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  // Atualizando as colunas para usar o navigate
  const updatedColumns = [
    { 
      key: 'name' as keyof Owner, 
      header: 'Nome',
      render: (owner: Owner) => (
        <button
          onClick={() => {
            // Salva o proprietário no localStorage para ser recuperado na página de detalhes
            localStorage.setItem('selectedOwner', JSON.stringify(owner))
            navigate(`/admin/proprietarios/${owner.id}`)
          }}
          className="text-primary-600 hover:text-primary-800"
        >
          {owner.name}
        </button>
      )
    },
    columns[1] // Mantém a coluna de ações
  ]

  const { data, isLoading, error } = useQuery({
    queryKey: ['owners'],
    queryFn: getOwners,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Owner> }) => updateOwner(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['owners'] })
      setIsEditModalOpen(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteOwner,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['owners'] })
    },
  })

  React.useEffect(() => {
    const handleOpenEdit = (event: CustomEvent) => {
      setSelectedOwner(event.detail)
      setIsEditModalOpen(true)
    }

    const handleDelete = (event: CustomEvent) => {
      if (confirm('Tem certeza que deseja excluir este proprietário?')) {
        deleteMutation.mutate(event.detail.id)
      }
    }

    window.addEventListener('openOwnerEdit', handleOpenEdit as EventListener)
    window.addEventListener('deleteOwner', handleDelete as EventListener)

    return () => {
      window.removeEventListener('openOwnerEdit', handleOpenEdit as EventListener)
      window.removeEventListener('deleteOwner', handleDelete as EventListener)
    }
  }, [deleteMutation])

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
          Erro ao carregar os proprietários. Por favor, tente novamente mais tarde.
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Proprietários</h1>
        <button className="btn btn-primary">
          Novo Proprietário
        </button>
      </div>
      <Table
        data={data?.data || []}
        columns={updatedColumns}
        className="shadow-sm"
      />

      {/* Modal de Edição */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Editar Proprietário"
      >
        {selectedOwner && (
          <form
            onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              const data = Object.fromEntries(formData.entries())
              updateMutation.mutate({ id: selectedOwner.id, data })
            }}
            className="space-y-4"
          >
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Nome
              </label>
              <input
                type="text"
                name="name"
                id="name"
                defaultValue={selectedOwner.name}
                className="input mt-1"
              />
            </div>
            <div className="mt-5 sm:mt-6">
              <button
                type="submit"
                className="btn btn-primary w-full"
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Salvando...' : 'Salvar'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  )
} 