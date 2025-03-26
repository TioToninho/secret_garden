import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
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

export function Dashboard() {
  const { data: bankReturnsData, isLoading: bankReturnsLoading } = useQuery({
    queryKey: ['currentMonthBankReturns'],
    queryFn: getCurrentMonthBankReturns
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

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* Card de Retornos Bancários */}
      <div className="bg-white shadow-md rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">
            Retornos Bancários - {getMonthName(new Date().getMonth() + 1)}
          </h2>
          <Link
            to="/admin/retornos-bancarios"
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            Ver todos
          </Link>
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
                      Data Pagamento
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
                  {bankReturnsData.data.slice(0, 5).map((bankReturn) => (
                    <tr key={bankReturn.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {bankReturn.client.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatDate(bankReturn.payment_date)}
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
                </tbody>
              </table>
            </div>

            <div className="mt-4 flex justify-between items-center pt-4 border-t border-gray-200">
              <div className="flex gap-4">
                <div>
                  <span className="block text-sm text-gray-500">Total de Retornos</span>
                  <span className="text-lg font-semibold text-gray-900">
                    {bankReturnsData.summary.total_returns}
                  </span>
                </div>
                <div>
                  <span className="block text-sm text-gray-500">Total Cobrado</span>
                  <span className="text-lg font-semibold text-gray-900">
                    {formatCurrency(bankReturnsData.summary.total_charged_amount)}
                  </span>
                </div>
                <div>
                  <span className="block text-sm text-gray-500">Total Oscilação</span>
                  <span className={`text-lg font-semibold ${bankReturnsData.summary.total_variation_amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(bankReturnsData.summary.total_variation_amount)}
                  </span>
                </div>
              </div>

              {bankReturnsData.data.length > 5 && (
                <Link
                  to="/admin/retornos-bancarios"
                  className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                >
                  Ver mais {bankReturnsData.data.length - 5} retornos
                </Link>
              )}
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">
              Nenhum retorno bancário registrado este mês.
            </p>
            <Link
              to="/admin/retornos-bancarios"
              className="inline-block mt-2 text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              Ver outros meses
            </Link>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Total de Clientes</h3>
          <p className="mt-2 text-3xl font-bold text-primary-600">0</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Total de Imóveis</h3>
          <p className="mt-2 text-3xl font-bold text-primary-600">0</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Receita Mensal</h3>
          <p className="mt-2 text-3xl font-bold text-primary-600">R$ 0,00</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900">Imóveis Disponíveis</h3>
          <p className="mt-2 text-3xl font-bold text-primary-600">0</p>
        </div>
      </div>
    </div>
  )
} 