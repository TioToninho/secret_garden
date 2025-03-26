import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Owner } from '@/services/api/owners'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import api from '@/services/api/axios'

interface Tenant {
  id: number
  name: string
}

interface MonthlyTransfer {
  id: number
  tenant: Tenant
  month: number
  year: number
  due_date: string | null
  rent_amount: number
  amount_paid: number | null
  payment_date: string | null
  condo_fee: number | null
  condo_paid_by_agency: boolean
  calculation_base: number
  percentage: number | null
  commission: number
  delivery_fee: number | null
  deposit_amount: number
  created_at: string
  updated_at: string
}

interface TransferSummary {
  total_rent: number
  total_commission: number
  total_condo_fees: number
  total_delivery_fees: number
  total_deposit: number
  total_properties: number
}

interface TransferMetadata {
  owner_id: number
  month: number
  year: number
  generated_at: string
}

interface MonthlyTransfersResponse {
  data: MonthlyTransfer[]
  summary: TransferSummary
  metadata: TransferMetadata
}

interface Client {
  id: number
  name: string
}

interface ClientsResponse {
  data: Client[]
  error: null | string
}

interface BankReturnPayload {
  payer_name: string
  due_date: string
  payment_date: string
  title_amount: number
  charged_amount: number
  variation_amount: number
}

interface BankReturn {
  id: number
  client: {
    id: number
    name: string
  }
  month: number
  year: number
  payer_name: string
  due_date: string
  payment_date: string
  title_amount: number
  charged_amount: number
  variation_amount: number
  created_at: string
  updated_at: string
}

interface BankReturnSummary {
  total_title_amount: number
  total_charged_amount: number
  total_variation_amount: number
  total_returns: number
}

interface BankReturnMetadata {
  owner_id: number
  month: number
  year: number
  generated_at: string
}

interface BankReturnsResponse {
  data: BankReturn[]
  summary: BankReturnSummary
  metadata: BankReturnMetadata
}

const getOwnerMonthlyTransfers = async (
  ownerId: number,
  month: number,
  year: number
): Promise<MonthlyTransfersResponse> => {
  try {
    const response = await api.get(
      `/api/monthly-transfers/owner/${ownerId}?month=${month}&year=${year}`
    )
    return response.data
  } catch (error) {
    console.error(`Erro ao buscar repasses mensais para o proprietário ${ownerId}:`, error)
    throw error
  }
}

const getOwnerClients = async (ownerId: number): Promise<ClientsResponse> => {
  try {
    const response = await api.get(`/api/owners/${ownerId}/clients`)
    return response.data
  } catch (error) {
    console.error(`Erro ao buscar clientes do proprietário ${ownerId}:`, error)
    throw error
  }
}

const createBankReturn = async (
  clientId: number,
  month: number,
  year: number,
  data: BankReturnPayload
): Promise<void> => {
  try {
    await api.post(`/api/bank-returns/client/${clientId}/${month}/${year}`, data)
  } catch (error) {
    console.error('Erro ao criar retorno bancário:', error)
    throw error
  }
}

const getOwnerBankReturns = async (
  ownerId: number,
  month: number,
  year: number
): Promise<BankReturnsResponse> => {
  try {
    const response = await api.get(
      `/api/bank-returns/owner/${ownerId}?month=${month}&year=${year}`
    )
    return response.data
  } catch (error) {
    console.error(`Erro ao buscar retornos bancários para o proprietário ${ownerId}:`, error)
    throw error
  }
}

export function OwnerDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1)
  const [year, setYear] = useState<number>(new Date().getFullYear())
  const [owner, setOwner] = useState<Owner | null>(null)
  
  // Estado para o formulário de retorno bancário
  const [selectedClient, setSelectedClient] = useState<number | ''>('')
  const [bankReturn, setBankReturn] = useState<Omit<BankReturnPayload, 'payer_name'>>({
    due_date: '',
    payment_date: '',
    title_amount: 0,
    charged_amount: 0,
    variation_amount: 0
  })

  useEffect(() => {
    const ownerData = localStorage.getItem('selectedOwner')
    if (ownerData) {
      setOwner(JSON.parse(ownerData))
    }
  }, [])
  
  const { 
    data: transfersData, 
    isLoading: transfersLoading, 
    error: transfersError,
    refetch: refetchTransfers
  } = useQuery({
    queryKey: ['ownerTransfers', id, month, year],
    queryFn: () => getOwnerMonthlyTransfers(Number(id), month, year),
    enabled: !!id,
  })
  
  // Query para buscar retornos bancários
  const { 
    data: bankReturnsData, 
    isLoading: bankReturnsLoading, 
    error: bankReturnsError 
  } = useQuery({
    queryKey: ['ownerBankReturns', id, month, year],
    queryFn: () => getOwnerBankReturns(Number(id), month, year),
    enabled: !!id
  })
  
  useEffect(() => {
    if (id) {
      refetchTransfers()
    }
  }, [month, year, id, refetchTransfers])
  
  const formatCurrency = (value: number | null) => {
    if (value === null) return 'Não informado'
    return `R$ ${value.toFixed(2)}`.replace('.', ',')
  }
  
  const formatDate = (date: string | null) => {
    if (!date) return 'Não informado'
    return new Date(date).toLocaleDateString('pt-BR')
  }
  
  const getMonthName = (monthNumber: number) => {
    const monthNames = [
      'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    return monthNames[monthNumber - 1]
  }
  
  const monthOptions = Array.from({ length: 12 }, (_, i) => i + 1).map(m => ({
    value: m,
    label: getMonthName(m)
  }))
  
  const currentYear = new Date().getFullYear()
  const yearOptions = Array.from({ length: 5 }, (_, i) => currentYear - i).map(y => ({
    value: y,
    label: y.toString()
  }))

  const exportToExcel = () => {
    if (!transfersData?.data || transfersData.data.length === 0) {
      alert('Não há dados para exportar.')
      return
    }
    
    const excelData = transfersData.data.map(transfer => ({
      'Nome do Locatário': transfer.tenant.name,
      'Data de Vencimento': transfer.due_date ? formatDate(transfer.due_date) : 'Não informado',
      'Valor do Aluguel': transfer.rent_amount,
      'Valor Pago': transfer.amount_paid || 0,
      'Condomínio': transfer.condo_fee || 0,
      'Pago pela Imobiliária': transfer.condo_paid_by_agency ? 'Sim' : 'Não',
      'Base de Cálculo': transfer.calculation_base,
      'Porcentagem': transfer.percentage ? `${transfer.percentage}%` : 'Não informado',
      'Comissão': transfer.commission,
      'Taxa de Envio': transfer.delivery_fee || 0,
      'Valor Depositado': transfer.deposit_amount,
      'Data de Pagamento': transfer.payment_date ? formatDate(transfer.payment_date) : 'Não informado'
    }))
    
    excelData.push({
      'Nome do Locatário': 'TOTAL',
      'Data de Vencimento': '',
      'Valor do Aluguel': transfersData.summary.total_rent,
      'Valor Pago': transfersData.data.reduce((sum, t) => sum + (t.amount_paid || 0), 0),
      'Condomínio': transfersData.summary.total_condo_fees,
      'Pago pela Imobiliária': '',
      'Base de Cálculo': transfersData.data.reduce((sum, t) => sum + t.calculation_base, 0),
      'Porcentagem': '',
      'Comissão': transfersData.summary.total_commission,
      'Taxa de Envio': transfersData.summary.total_delivery_fees,
      'Valor Depositado': transfersData.summary.total_deposit,
      'Data de Pagamento': ''
    })
    
    const worksheet = XLSX.utils.json_to_sheet(excelData)
    
    const columnWidths = [
      { wch: 30 }, // Nome do Locatário
      { wch: 20 }, // Data de Vencimento
      { wch: 15 }, // Valor do Aluguel
      { wch: 15 }, // Valor Pago
      { wch: 15 }, // Condomínio
      { wch: 20 }, // Pago pela Imobiliária
      { wch: 15 }, // Base de Cálculo
      { wch: 15 }, // Porcentagem
      { wch: 15 }, // Comissão
      { wch: 15 }, // Taxa de Envio
      { wch: 15 }, // Valor Depositado
      { wch: 20 }  // Data de Pagamento
    ]
    worksheet['!cols'] = columnWidths
    
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Repasse Mensal')
    
    const ownerName = owner?.name || `Proprietario_${id}`
    const fileName = `${ownerName}_Repasse_${getMonthName(month)}_${year}.xlsx`
    
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' })
    saveAs(blob, fileName)
  }

  // Query para buscar clientes do proprietário
  const { 
    data: clientsData,
    isLoading: clientsLoading
  } = useQuery({
    queryKey: ['ownerClients', id],
    queryFn: () => getOwnerClients(Number(id)),
    enabled: !!id
  })

  // Mutation para criar retorno bancário
  const createBankReturnMutation = useMutation({
    mutationFn: (data: { clientId: number, payload: BankReturnPayload }) => 
      createBankReturn(data.clientId, month, year, data.payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ownerTransfers', id, month, year] })
      // Resetar formulário
      setSelectedClient('')
      setBankReturn({
        due_date: '',
        payment_date: '',
        title_amount: 0,
        charged_amount: 0,
        variation_amount: 0
      })
    }
  })

  const handleBankReturnSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!selectedClient) {
      alert('Por favor, selecione um locatário')
      return
    }

    const selectedClientData = clientsData?.data.find(c => c.id === selectedClient)
    if (!selectedClientData) return

    const payload: BankReturnPayload = {
      payer_name: selectedClientData.name,
      ...bankReturn
    }

    createBankReturnMutation.mutate({ 
      clientId: selectedClient,
      payload
    })
  }

  const handleBankReturnChange = (field: keyof Omit<BankReturnPayload, 'payer_name'>) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = field.includes('amount') 
      ? parseFloat(e.target.value) || 0
      : e.target.value

    setBankReturn(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const exportBankReturnsToExcel = () => {
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
    
    const ownerName = owner?.name || `Proprietario_${id}`
    const fileName = `${ownerName}_Retornos_${getMonthName(month)}_${year}.xlsx`
    
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' })
    saveAs(blob, fileName)
  }

  if (transfersLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <button 
          onClick={() => navigate('/admin/proprietarios')}
          className="mr-4 text-gray-600 hover:text-gray-900"
        >
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </button>
        <h1 className="text-2xl font-bold text-gray-900">
          Detalhes do Proprietário {owner ? `- ${owner.name}` : `#${id}`}
        </h1>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex flex-col">
            <label htmlFor="month" className="block text-sm font-medium text-gray-700 mb-1">
              Mês
            </label>
            <select
              id="month"
              className="input max-w-[200px]"
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
            >
              {monthOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex flex-col">
            <label htmlFor="year" className="block text-sm font-medium text-gray-700 mb-1">
              Ano
            </label>
            <select
              id="year"
              className="input max-w-[200px]"
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
            >
              {yearOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="md:ml-auto flex items-end gap-4">
            {transfersData && (
              <>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-gray-500">Total a Depositar</span>
                  <span className="text-lg font-bold text-primary-600">
                    {formatCurrency(transfersData.summary.total_deposit)}
                  </span>
                </div>
                
                <div className="flex gap-2">
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
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">
            Repasse Mensal - {getMonthName(month)} de {year}
          </h2>
        </div>
        
        {transfersError ? (
          <div className="bg-red-50 p-4 rounded-md mb-6">
            <p className="text-red-600">
              Erro ao carregar os repasses mensais. Por favor, tente novamente mais tarde.
            </p>
          </div>
        ) : transfersData?.data && transfersData.data.length > 0 ? (
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Locatário
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Vencimento
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Aluguel
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor Pago
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Condomínio
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Base Cálculo
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      %
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Comissão
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Taxa Envio
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Valor Depositado
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {transfersData.data.map((transfer) => (
                    <tr key={transfer.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {transfer.tenant.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {transfer.due_date ? formatDate(transfer.due_date) : 'Não informado'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(transfer.rent_amount)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(transfer.amount_paid)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatCurrency(transfer.condo_fee)}
                          {transfer.condo_paid_by_agency && (
                            <span className="ml-1 text-xs text-primary-600" title="Pago pela imobiliária">
                              (Imob.)
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(transfer.calculation_base)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {transfer.percentage ? `${transfer.percentage}%` : '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(transfer.commission)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(transfer.delivery_fee)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{formatCurrency(transfer.deposit_amount)}</div>
                      </td>
                    </tr>
                  ))}
                  <tr className="bg-gray-50 font-semibold">
                    <td className="px-6 py-4 whitespace-nowrap" colSpan={2}>
                      <div className="text-sm font-bold text-gray-900">TOTAL</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(transfersData.summary.total_rent)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(transfersData.data.reduce((sum, t) => sum + (t.amount_paid || 0), 0))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(transfersData.summary.total_condo_fees)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(transfersData.data.reduce((sum, t) => sum + t.calculation_base, 0))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">-</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(transfersData.summary.total_commission)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(transfersData.summary.total_delivery_fees)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {formatCurrency(transfersData.summary.total_deposit)}
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-50 p-4 rounded-lg">
            <p className="text-yellow-700">
              Nenhum repasse mensal encontrado para este proprietário no período selecionado.
            </p>
          </div>
        )}
      </div>

      {/* Retornos Bancários */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">
            Retornos Bancários - {getMonthName(month)} de {year}
          </h2>
          {bankReturnsData?.data && bankReturnsData.data.length > 0 && (
            <button 
              onClick={exportBankReturnsToExcel}
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
        
        {bankReturnsError ? (
          <div className="bg-red-50 p-4 rounded-md mb-6">
            <p className="text-red-600">
              Erro ao carregar os retornos bancários. Por favor, tente novamente mais tarde.
            </p>
          </div>
        ) : bankReturnsData?.data && bankReturnsData.data.length > 0 ? (
          <div className="bg-white shadow-md rounded-lg overflow-hidden">
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
          </div>
        ) : (
          <div className="bg-yellow-50 p-4 rounded-lg">
            <p className="text-yellow-700">
              Nenhum retorno bancário encontrado para este proprietário no período selecionado.
            </p>
          </div>
        )}
      </div>

      {/* Formulário de Retorno Bancário */}
      <div className="bg-white shadow-md rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Adicionar Retorno</h3>
        
        <form onSubmit={handleBankReturnSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label htmlFor="client" className="block text-sm font-medium text-gray-700 mb-1">
                Locatário
              </label>
              <select
                id="client"
                className="input w-full"
                value={selectedClient}
                onChange={(e) => setSelectedClient(Number(e.target.value))}
                required
              >
                <option value="">Selecione um locatário</option>
                {clientsData?.data.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 mb-1">
                Data de Vencimento
              </label>
              <input
                type="date"
                id="due_date"
                className="input w-full"
                value={bankReturn.due_date}
                onChange={handleBankReturnChange('due_date')}
                required
              />
            </div>

            <div>
              <label htmlFor="payment_date" className="block text-sm font-medium text-gray-700 mb-1">
                Data de Pagamento
              </label>
              <input
                type="date"
                id="payment_date"
                className="input w-full"
                value={bankReturn.payment_date}
                onChange={handleBankReturnChange('payment_date')}
                required
              />
            </div>

            <div>
              <label htmlFor="title_amount" className="block text-sm font-medium text-gray-700 mb-1">
                Valor do Título
              </label>
              <input
                type="number"
                id="title_amount"
                className="input w-full"
                value={bankReturn.title_amount}
                onChange={handleBankReturnChange('title_amount')}
                step="0.01"
                min="0"
                required
              />
            </div>

            <div>
              <label htmlFor="charged_amount" className="block text-sm font-medium text-gray-700 mb-1">
                Valor Cobrado
              </label>
              <input
                type="number"
                id="charged_amount"
                className="input w-full"
                value={bankReturn.charged_amount}
                onChange={handleBankReturnChange('charged_amount')}
                step="0.01"
                min="0"
                required
              />
            </div>

            <div>
              <label htmlFor="variation_amount" className="block text-sm font-medium text-gray-700 mb-1">
                Valor Oscilação
              </label>
              <input
                type="number"
                id="variation_amount"
                className="input w-full"
                value={bankReturn.variation_amount}
                onChange={handleBankReturnChange('variation_amount')}
                step="0.01"
                required
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={createBankReturnMutation.isPending}
            >
              {createBankReturnMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Salvando...
                </>
              ) : (
                'Adicionar Retorno'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
} 