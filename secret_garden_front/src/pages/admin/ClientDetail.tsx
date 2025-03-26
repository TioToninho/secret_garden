import React, { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getClientDetail, updateClient, ClientDetail } from '@/services/api/clients'
import { getClientMonthlyCalculations, MonthlyCalculation } from '@/services/api/monthlyCalculations'
import { 
  getClientMonthlyVariableValues, 
  MonthlyVariableValue 
} from '@/services/api/monthlyValues'

export function ClientDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState<Partial<ClientDetail>>({})

  const { data, isLoading, error } = useQuery({
    queryKey: ['clientDetail', id],
    queryFn: () => getClientDetail(Number(id)),
    enabled: !!id,
  })

  const { 
    data: calculationsData, 
    isLoading: calculationsLoading, 
    error: calculationsError 
  } = useQuery({
    queryKey: ['clientCalculations', id],
    queryFn: () => getClientMonthlyCalculations(Number(id)),
    enabled: !!id,
  })

  const {
    data: variableValuesData,
    isLoading: variableValuesLoading,
    error: variableValuesError
  } = useQuery({
    queryKey: ['clientVariableValues', id],
    queryFn: () => getClientMonthlyVariableValues(Number(id)),
    enabled: !!id,
  })

  const updateMutation = useMutation({
    mutationFn: (data: Partial<ClientDetail>) => 
      updateClient(Number(id), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clientDetail', id] })
      queryClient.invalidateQueries({ queryKey: ['clientNames'] })
      setIsEditing(false)
    },
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement
    
    let parsedValue: any = value
    if (type === 'number') {
      parsedValue = parseFloat(value)
    } else if (type === 'checkbox') {
      parsedValue = (e.target as HTMLInputElement).checked
    }
    
    setFormData(prev => ({ ...prev, [name]: parsedValue }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateMutation.mutate(formData)
  }

  const startEditing = () => {
    if (data?.data) {
      setFormData({
        name: data.data.name,
        status: data.data.status,
        due_date: data.data.due_date,
        amount_paid: data.data.amount_paid,
        condo_fee: data.data.condo_fee,
        percentage: data.data.percentage,
        delivery_fee: data.data.delivery_fee,
        start_date: data.data.start_date,
        condo_paid: data.data.condo_paid,
        is_active: data.data.is_active,
      })
      setIsEditing(true)
    }
  }

  const formatCurrency = (value: number | null) => {
    if (value === null) return 'Não informado'
    return `R$ ${value.toFixed(2)}`.replace('.', ',')
  }

  const getMonthName = (month: number) => {
    const monthNames = [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    return monthNames[month - 1]
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <div className="flex items-center mb-6">
          <button 
            onClick={() => navigate('/admin/clientes')}
            className="mr-4 text-gray-600 hover:text-gray-900"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </button>
          <h1 className="text-2xl font-bold text-gray-900">Detalhes do Cliente</h1>
        </div>
        
        <div className="bg-red-50 p-4 rounded-md">
          <p className="text-red-600">
            Erro ao carregar os detalhes do cliente. Por favor, tente novamente mais tarde.
          </p>
        </div>
      </div>
    )
  }

  const client = data.data

  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <button 
          onClick={() => navigate('/admin/clientes')}
          className="mr-4 text-gray-600 hover:text-gray-900"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">Detalhes do Cliente</h1>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        {!isEditing ? (
          <>
            <div className="flex justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-800">{client.name}</h2>
              <button 
                onClick={startEditing}
                className="btn btn-primary"
              >
                Editar Cliente
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-md font-medium text-gray-700 mb-4">Informações Básicas</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-500">ID do Proprietário</p>
                    <p className="text-base">{client.owner_id}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Status</p>
                    <p className="text-base">{client.status}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Data de Início</p>
                    <p className="text-base">{new Date(client.start_date).toLocaleDateString('pt-BR')}</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-md font-medium text-gray-700 mb-4">Informações Financeiras</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Dia de Vencimento</p>
                    <p className="text-base">{client.due_date}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Valor Pago</p>
                    <p className="text-base">R$ {client.amount_paid.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Valor do Condomínio</p>
                    <p className="text-base">R$ {client.condo_fee.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Porcentagem</p>
                    <p className="text-base">{client.percentage}%</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Taxa de Entrega</p>
                    <p className="text-base">R$ {client.delivery_fee.toFixed(2)}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex items-center space-x-6">
                <div className="flex items-center">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${client.condo_paid ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  <span className="text-sm font-medium text-gray-700">
                    Condomínio {client.condo_paid ? 'Pago' : 'Pendente'}
                  </span>
                </div>
                <div className="flex items-center">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${client.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  <span className="text-sm font-medium text-gray-700">
                    {client.is_active ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
              </div>
            </div>
          </>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="flex justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-800">Editar Cliente</h2>
              <div className="space-x-2">
                <button 
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="btn btn-outline"
                >
                  Cancelar
                </button>
                <button 
                  type="submit"
                  className="btn btn-primary"
                  disabled={updateMutation.isPending}
                >
                  {updateMutation.isPending ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                    Nome
                  </label>
                  <input
                    type="text"
                    name="name"
                    id="name"
                    className="input mt-1"
                    value={formData.name || ''}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                    Status
                  </label>
                  <input
                    type="text"
                    name="status"
                    id="status"
                    className="input mt-1"
                    value={formData.status || ''}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">
                    Data de Início
                  </label>
                  <input
                    type="date"
                    name="start_date"
                    id="start_date"
                    className="input mt-1"
                    value={formData.start_date ? formData.start_date.split('T')[0] : ''}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label htmlFor="due_date" className="block text-sm font-medium text-gray-700">
                    Dia de Vencimento
                  </label>
                  <input
                    type="number"
                    name="due_date"
                    id="due_date"
                    className="input mt-1"
                    value={formData.due_date || 0}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label htmlFor="amount_paid" className="block text-sm font-medium text-gray-700">
                    Valor Pago
                  </label>
                  <input
                    type="number"
                    name="amount_paid"
                    id="amount_paid"
                    step="0.01"
                    className="input mt-1"
                    value={formData.amount_paid || 0}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label htmlFor="condo_fee" className="block text-sm font-medium text-gray-700">
                    Valor do Condomínio
                  </label>
                  <input
                    type="number"
                    name="condo_fee"
                    id="condo_fee"
                    step="0.01"
                    className="input mt-1"
                    value={formData.condo_fee || 0}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label htmlFor="percentage" className="block text-sm font-medium text-gray-700">
                    Porcentagem
                  </label>
                  <input
                    type="number"
                    name="percentage"
                    id="percentage"
                    step="0.01"
                    className="input mt-1"
                    value={formData.percentage || 0}
                    onChange={handleChange}
                  />
                </div>
                <div>
                  <label htmlFor="delivery_fee" className="block text-sm font-medium text-gray-700">
                    Taxa de Entrega
                  </label>
                  <input
                    type="number"
                    name="delivery_fee"
                    id="delivery_fee"
                    step="0.01"
                    className="input mt-1"
                    value={formData.delivery_fee || 0}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200 flex items-center space-x-6">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="condo_paid"
                  id="condo_paid"
                  checked={formData.condo_paid || false}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="condo_paid" className="ml-2 block text-sm text-gray-900">
                  Condomínio Pago
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="is_active"
                  id="is_active"
                  checked={formData.is_active || false}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                  Ativo
                </label>
              </div>
            </div>
          </form>
        )}
      </div>

      {/* Valores Mensais Variáveis */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Valores Mensais Variáveis</h2>

        {variableValuesLoading ? (
          <div className="flex items-center justify-center h-24 bg-white shadow-md rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : variableValuesError ? (
          <div className="bg-red-50 p-4 rounded-md mb-6">
            <p className="text-red-600">
              Erro ao carregar os valores mensais variáveis. Por favor, tente novamente mais tarde.
            </p>
          </div>
        ) : variableValuesData?.data && variableValuesData.data.length > 0 ? (
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Período
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Conta de Água
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Conta de Gás
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Seguro
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      IPTU
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Taxa de Condomínio
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {variableValuesData.data.map((valueItem: MonthlyVariableValue) => (
                    <tr key={valueItem.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {getMonthName(valueItem.month)} de {valueItem.year}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(valueItem.water_bill)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(valueItem.gas_bill)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(valueItem.insurance)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(valueItem.property_tax)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(valueItem.condo_fee)}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 p-4 rounded-lg">
            <p className="text-yellow-700">
              Nenhum valor mensal variável encontrado para este cliente.
            </p>
          </div>
        )}
      </div>

      {/* Cálculos Mensais */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Cálculos Mensais</h2>

        {calculationsLoading ? (
          <div className="flex items-center justify-center h-24 bg-white shadow-md rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : calculationsError ? (
          <div className="bg-red-50 p-4 rounded-md mb-6">
            <p className="text-red-600">
              Erro ao carregar os cálculos mensais. Por favor, tente novamente mais tarde.
            </p>
          </div>
        ) : calculationsData?.data && calculationsData.data.length > 0 ? (
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Período
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor do Aluguel
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Base de Cálculo
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pagamento Inquilino
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Comissão
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor do Depósito
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {calculationsData.data.map((calculation: MonthlyCalculation) => (
                    <tr key={calculation.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {getMonthName(calculation.month)} de {calculation.year}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(calculation.rent_amount)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(calculation.calculation_base)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(calculation.tenant_payment)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(calculation.commission)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(calculation.deposit_amount)}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 p-4 rounded-lg">
            <p className="text-yellow-700">
              Nenhum cálculo mensal encontrado para este cliente.
            </p>
          </div>
        )}
      </div>
    </div>
  )
} 