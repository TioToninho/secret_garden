export function PropertyManagement() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Gerenciamento de Imóveis</h1>
        <button className="btn btn-primary">
          Novo Imóvel
        </button>
      </div>
      <p className="text-gray-600 mb-6">
        Gerencie todos os imóveis cadastrados no sistema.
      </p>
      <div className="bg-white shadow-sm rounded-lg">
        <div className="p-4 border-b border-gray-200">
          <p className="text-gray-500">Nenhum imóvel cadastrado.</p>
        </div>
      </div>
    </div>
  )
} 