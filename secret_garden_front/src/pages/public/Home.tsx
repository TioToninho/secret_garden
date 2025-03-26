import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getNextAdjustments, AdjustmentItem } from '@/services/api/adjustments'
import { getHealthStatus } from '@/services/api/health'
import { 
  getPendingMonthlyValues, 
  updateMonthlyValues, 
  PendingMonthlyValue, 
  MonthlyVariableValueUpdate 
} from '@/services/api/monthlyValues'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import api from '@/services/api/axios'

interface Client {
  id: number
  name: string
}

interface BankReturn {
  id: number
  client: Client
  month: number
  year: number
  payer_name: string
  due_date: string
  payment_date: string
  title_amount: number
  charged_amount: number
  variation_amount: number
}

interface BankReturnSummary {
  total_title_amount: number
  total_charged_amount: number
  total_variation_amount: number
  total_returns: number
}

interface BankReturnsResponse {
  data: BankReturn[]
  summary: BankReturnSummary
  metadata: {
    month: number
    year: number
    generated_at: string
  }
}

const getCurrentMonthBankReturns = async (): Promise<BankReturnsResponse> => {
  const currentDate = new Date()
  const month = currentDate.getMonth() + 1
  const year = currentDate.getFullYear()
  
  const response = await api.get(`/api/bank-returns/month/${month}/${year}`)
  return response.data
}

export function Home() {
  const [currentDate] = useState(new Date())
  const [activeClient, setActiveClient] = useState<PendingMonthlyValue | null>(null)
  const [formValues, setFormValues] = useState<MonthlyVariableValueUpdate>({})
  const queryClient = useQueryClient()
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['nextAdjustments'],
    queryFn: getNextAdjustments,
  })

  const { 
    data: healthData, 
    isLoading: healthLoading, 
    error: healthError 
  } = useQuery({
    queryKey: ['healthStatus'],
    queryFn: getHealthStatus,
  })

  const {
    data: pendingValues,
    isLoading: pendingLoading,
    error: pendingError
  } = useQuery({
    queryKey: ['pendingMonthlyValues'],
    queryFn: getPendingMonthlyValues,
  })

  const { 
    data: bankReturnsData, 
    isLoading: bankReturnsLoading 
  } = useQuery({
    queryKey: ['currentMonthBankReturns'],
    queryFn: getCurrentMonthBankReturns
  })

  const updateMutation = useMutation({
    mutationFn: (data: { clientId: number; month: number; year: number; values: MonthlyVariableValueUpdate }) => 
      updateMonthlyValues(data.clientId, data.month, data.year, data.values),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingMonthlyValues'] })
      setActiveClient(null)
      setFormValues({})
    }
  })

  const formatCurrency = (value: number) => {
    return `R$ ${value.toFixed(2)}`.replace('.', ',')
  }

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('pt-BR')
  }

  // Formatar a data atual
  const formattedDate = currentDate.toLocaleDateString('pt-BR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })

  // Primeira letra maiúscula
  const capitalizedDate = formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1)

  // Função para obter cor baseada no status
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'ok':
      case 'healthy':
      case 'up':
        return 'text-green-500'
      case 'warning':
        return 'text-yellow-500'
      case 'error':
      case 'down':
        return 'text-red-500'
      default:
        return 'text-gray-500'
    }
  }

  // Traduzir nomes dos campos
  const getFieldTranslation = (field: string): string => {
    const translations: Record<string, string> = {
      'water_bill': 'Conta de Água',
      'gas_bill': 'Conta de Gás',
      'insurance': 'Seguro',
      'property_tax': 'IPTU',
      'condo_fee': 'Taxa de Condomínio'
    }
    return translations[field] || field
  }

  const handleInputChange = (field: string, value: string) => {
    const numValue = value === '' ? undefined : parseFloat(value)
    setFormValues(prev => ({ ...prev, [field]: numValue }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (activeClient && Object.keys(formValues).length > 0) {
      // Filtra campos vazios antes de enviar
      const valuesToSend = Object.fromEntries(
        Object.entries(formValues).filter(([_, value]) => value !== undefined)
      )
      
      if (Object.keys(valuesToSend).length > 0) {
        updateMutation.mutate({
          clientId: activeClient.id,
          month: activeClient.month,
          year: activeClient.year,
          values: valuesToSend as MonthlyVariableValueUpdate
        })
      }
    }
  }

  const monthNames = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ]

  const exportToExcel = () => {
    if (!bankReturnsData?.data || bankReturnsData.data.length === 0) {
      alert('Não há dados para exportar.')
      return
    }
    
    const excelData = bankReturnsData.data.map(bankReturn => ({
      'Locatário': bankReturn.client.name,
      'Pagador': bankReturn.payer_name,
      'Data de Vencimento': formatDate(bankReturn.due_date),
      'Data de Pagamento': formatDate(bankReturn.payment_date),
      'Valor do Título': bankReturn.title_amount,
      'Valor Cobrado': bankReturn.charged_amount,
      'Oscilação': bankReturn.variation_amount
    }))
    
    excelData.push({
      'Locatário': 'TOTAL',
      'Pagador': '',
      'Data de Vencimento': '',
      'Data de Pagamento': '',
      'Valor do Título': bankReturnsData.summary.total_title_amount,
      'Valor Cobrado': bankReturnsData.summary.total_charged_amount,
      'Oscilação': bankReturnsData.summary.total_variation_amount
    })
    
    const worksheet = XLSX.utils.json_to_sheet(excelData)
    
    const columnWidths = [
      { wch: 30 }, // Locatário
      { wch: 30 }, // Pagador
      { wch: 20 }, // Data de Vencimento
      { wch: 20 }, // Data de Pagamento
      { wch: 15 }, // Valor do Título
      { wch: 15 }, // Valor Cobrado
      { wch: 15 }  // Oscilação
    ]
    worksheet['!cols'] = columnWidths
    
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Retornos Bancários')
    
    const fileName = `Retornos_Bancarios_${monthNames[currentDate.getMonth()]}_${currentDate.getFullYear()}.xlsx`
    
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' })
    saveAs(blob, fileName)
  }

  return (
    <div className="p-6">
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Secret Garden</h1>
        <p className="text-lg text-gray-500">{capitalizedDate}</p>
      </div>

      {/* Valores Mensais Pendentes */}
      {pendingValues?.data && pendingValues.data.length > 0 && (
        <>
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Valores Mensais Pendentes</h2>
          
          {pendingLoading ? (
            <div className="flex items-center justify-center h-24">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : pendingError ? (
            <div className="bg-red-50 p-4 rounded-md mb-6">
              <p className="text-red-600">
                Erro ao carregar valores mensais pendentes. Por favor, tente novamente mais tarde.
              </p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-5 mb-10">
              {activeClient ? (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">{activeClient.name}</h3>
                      <p className="text-sm text-gray-500">
                        {monthNames[activeClient.month - 1]} de {activeClient.year}
                      </p>
                    </div>
                    <button 
                      onClick={() => {
                        setActiveClient(null)
                        setFormValues({})
                      }}
                      className="text-gray-500 hover:text-gray-700"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-4">
                    Preencha apenas os campos que você deseja atualizar. Campos vazios serão ignorados.
                  </p>
                  
                  <form onSubmit={handleSubmit} className="space-y-4">
                    {activeClient.empty_fields.map((field) => (
                      <div key={field}>
                        <label htmlFor={field} className="block text-sm font-medium text-gray-700">
                          {getFieldTranslation(field)}
                        </label>
                        <input
                          type="number"
                          id={field}
                          name={field}
                          step="0.01"
                          value={formValues[field] !== undefined ? formValues[field] : ''}
                          onChange={(e) => handleInputChange(field, e.target.value)}
                          className="input mt-1"
                          placeholder={`Valor para ${getFieldTranslation(field)}`}
                        />
                      </div>
                    ))}
                    
                    <div className="flex justify-end mt-4">
                      <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={updateMutation.isPending || Object.keys(formValues).length === 0}
                      >
                        {updateMutation.isPending ? 'Salvando...' : 'Salvar'}
                      </button>
                    </div>
                  </form>
                </div>
              ) : (
                <div>
                  <p className="mb-4">Clientes com valores mensais pendentes a serem preenchidos:</p>
                  <ul className="divide-y divide-gray-200">
                    {pendingValues.data.map((client) => (
                      <li key={`${client.id}-${client.month}-${client.year}`} className="py-3">
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="font-medium text-gray-800">{client.name}</p>
                            <p className="text-sm text-gray-500">
                              {monthNames[client.month - 1]} de {client.year}
                            </p>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {client.pending_fields.map((field, index) => (
                                <span key={index} className="inline-block px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                                  {field}
                                </span>
                              ))}
                            </div>
                          </div>
                          <button
                            onClick={() => setActiveClient(client)}
                            className="btn btn-sm btn-outline"
                          >
                            Preencher
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </>
      )}

      <h2 className="text-2xl font-semibold text-gray-800 mb-6">Próximos Ajustes</h2>
      
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 p-4 rounded-md mb-6">
          <p className="text-red-600">
            Erro ao carregar os próximos ajustes. Por favor, tente novamente mais tarde.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          {data && Object.entries(data.data).map(([monthYear, adjustments]) => {
            const [month, year] = monthYear.split('/')
            const monthName = monthNames[parseInt(month) - 1]
            
            return (
              <div key={monthYear} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="bg-primary-600 text-white py-3 px-4">
                  <h3 className="font-semibold">{monthName} de {year}</h3>
                </div>
                <div className="p-4">
                  {adjustments.length === 0 ? (
                    <p className="text-gray-500 italic">Nenhum ajuste previsto</p>
                  ) : (
                    <ul className="divide-y divide-gray-200">
                      {adjustments.map((adjustment: AdjustmentItem) => (
                        <li key={adjustment.id} className="py-3">
                          <p className="font-medium text-gray-800">{adjustment.name}</p>
                          <p className="text-sm text-gray-500">
                            Ajuste em: {new Date(adjustment.next_adjustment).toLocaleDateString('pt-BR')}
                          </p>
                          <p className="text-xs text-gray-400">
                            Data inicial: {new Date(adjustment.start_date).toLocaleDateString('pt-BR')}
                          </p>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )
          })}
          
          {data && Object.keys(data.data).length === 0 && (
            <div className="col-span-full bg-yellow-50 p-4 rounded-md">
              <p className="text-yellow-700">
                Não há ajustes previstos para os próximos 3 meses.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Card de Retornos Bancários */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-10">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Retornos Bancários - {monthNames[currentDate.getMonth()]}
          </h2>
          <div className="flex items-center gap-2">
            <button 
              onClick={() => window.location.href = '/admin/retornos-bancarios'}
              className="btn btn-primary btn-sm"
              title="Ver todos os retornos"
            >
              Ver Todos
            </button>
            {bankReturnsData?.data && bankReturnsData.data.length > 0 && (
              <button 
                onClick={exportToExcel}
                className="btn btn-outline btn-sm flex items-center gap-1"
                title="Exportar para Excel"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Excel
              </button>
            )}
          </div>
        </div>

        {bankReturnsLoading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : bankReturnsData?.data && bankReturnsData.data.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Locatário
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pagador
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vencimento
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data Pagamento
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor Título
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor Cobrado
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Oscilação
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {bankReturnsData.data.map((bankReturn) => (
                    <tr key={bankReturn.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {bankReturn.client.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {bankReturn.payer_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatDate(bankReturn.due_date)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatDate(bankReturn.payment_date)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatCurrency(bankReturn.title_amount)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatCurrency(bankReturn.charged_amount)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-sm ${bankReturn.variation_amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {formatCurrency(bankReturn.variation_amount)}
                        </div>
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-gray-50 font-semibold">
                    <td className="px-6 py-4 whitespace-nowrap" colSpan={4}>
                      <div className="text-sm font-bold text-gray-900">TOTAL</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(bankReturnsData.summary.total_title_amount)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(bankReturnsData.summary.total_charged_amount)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm ${bankReturnsData.summary.total_variation_amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {formatCurrency(bankReturnsData.summary.total_variation_amount)}
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">
              Nenhum retorno bancário registrado este mês.
            </p>
          </div>
        )}
      </div>

      {/* Health Check Section */}
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Status do Sistema</h2>
      
      {healthLoading ? (
        <div className="flex items-center justify-center h-24">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : healthError ? (
        <div className="bg-red-50 p-4 rounded-md">
          <p className="text-red-600">
            Erro ao verificar o status do sistema. Por favor, tente novamente mais tarde.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-5 mb-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Status Geral */}
            <div className="flex items-center space-x-3 p-3 border rounded-lg">
              <div className={`text-xl ${getStatusColor(healthData?.overall || 'unknown')}`}>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Status Geral</p>
                <p className={`text-sm ${getStatusColor(healthData?.overall || 'unknown')}`}>
                  {healthData?.overall === 'ok' ? 'Funcionando' : healthData?.overall || 'Desconhecido'}
                </p>
              </div>
            </div>

            {/* API */}
            <div className="flex items-center space-x-3 p-3 border rounded-lg">
              <div className={`text-xl ${getStatusColor(healthData?.api?.status || 'unknown')}`}>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">API</p>
                <p className={`text-sm ${getStatusColor(healthData?.api?.status || 'unknown')}`}>
                  {healthData?.api?.status === 'ok' ? 'Funcionando' : healthData?.api?.status || 'Desconhecido'}
                </p>
                {healthData?.api?.message && (
                  <p className="text-xs text-gray-500 mt-1">
                    {healthData.api.message}
                  </p>
                )}
              </div>
            </div>

            {/* Banco de Dados */}
            <div className="flex items-center space-x-3 p-3 border rounded-lg">
              <div className={`text-xl ${getStatusColor(healthData?.database?.status || 'unknown')}`}>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Banco de Dados</p>
                <p className={`text-sm ${getStatusColor(healthData?.database?.status || 'unknown')}`}>
                  {healthData?.database?.status === 'ok' ? 'Funcionando' : healthData?.database?.status || 'Desconhecido'}
                </p>
                {healthData?.database?.message && (
                  <p className="text-xs text-gray-500 mt-1">
                    {healthData.database.message}
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="mt-4 text-xs text-gray-500 text-right">
            Atualizado em: {new Date().toLocaleTimeString('pt-BR')}
          </div>
        </div>
      )}
    </div>
  )
} 