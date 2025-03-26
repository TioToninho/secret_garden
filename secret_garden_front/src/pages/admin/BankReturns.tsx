import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
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
  month: number
  year: number
  generated_at: string
}

interface BankReturnsResponse {
  data: BankReturn[]
  summary: BankReturnSummary
  metadata: BankReturnMetadata
}

const getMonthlyBankReturns = async (
  month: number,
  year: number
): Promise<BankReturnsResponse> => {
  try {
    const response = await api.get(`/api/bank-returns/month/${month}/${year}`)
    return response.data
  } catch (error) {
    console.error('Erro ao buscar retornos bancários:', error)
    throw error
  }
}

export function BankReturnsPage() {
  const [month, setMonth] = useState<number>(new Date().getMonth() + 1)
  const [year, setYear] = useState<number>(new Date().getFullYear())

  const { 
    data: bankReturnsData, 
    isLoading: bankReturnsLoading, 
    error: bankReturnsError 
  } = useQuery({
    queryKey: ['monthlyBankReturns', month, year],
    queryFn: () => getMonthlyBankReturns(month, year)
  })

  const formatCurrency = (value: number) => {
    return `R$ ${value.toFixed(2)}`.replace('.', ',')
  }

  const formatDate = (date: string) => {
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
    
    const fileName = `Retornos_Bancarios_${getMonthName(month)}_${year}.xlsx`
    
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' })
    saveAs(blob, fileName)
  }

  if (bankReturnsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Retornos Bancários
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
            {bankReturnsData && (
              <>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-gray-500">Total de Retornos</span>
                  <span className="text-lg font-bold text-primary-600">
                    {bankReturnsData.summary.total_returns}
                  </span>
                </div>
                
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
              </>
            )}
          </div>
        </div>
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
            Nenhum retorno bancário encontrado para o período selecionado.
          </p>
        </div>
      )}
    </div>
  )
} 