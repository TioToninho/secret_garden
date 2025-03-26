export interface Client {
  id: number
  name: string
  owner_id: number
  status: string
  due_date: number
  amount_paid: number
  property_tax: number
  interest: number
  utilities: number
  insurance: number
  condo_fee: number
  percentage: number
  delivery_fee: number
  start_date: string
  condo_paid: boolean
  withdrawal_date: string | null
  withdrawal_number: string | null
  payment_date: string | null
  notes: string | null
  has_monthly_variation: boolean
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface ClientResponse {
  data: Client[]
  error: string | null
} 