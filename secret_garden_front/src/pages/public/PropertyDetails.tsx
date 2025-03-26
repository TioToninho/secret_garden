import { useParams } from 'react-router-dom'

export function PropertyDetails() {
  const { id } = useParams()

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Detalhes do Imóvel</h1>
      <p className="text-gray-600">
        Detalhes do imóvel com ID: {id}
      </p>
    </div>
  )
} 