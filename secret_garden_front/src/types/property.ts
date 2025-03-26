export interface Property {
  id: number
  title: string
  description: string
  price: number
  address: string
  city: string
  state: string
  bedrooms: number
  bathrooms: number
  area: number
  type: 'CASA' | 'APARTAMENTO' | 'COMERCIAL' | 'TERRENO'
  status: 'DISPONIVEL' | 'VENDIDO' | 'ALUGADO'
  images: string[]
  features: string[]
  createdAt: string
  updatedAt: string
}

export interface PropertyFilters {
  type?: Property['type']
  status?: Property['status']
  minPrice?: number
  maxPrice?: number
  bedrooms?: number
  city?: string
  state?: string
} 