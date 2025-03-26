import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { AdminLayout } from './components/layout/AdminLayout'
import { Home } from './pages/public/Home'
import { Properties } from './pages/public/Properties'
import { PropertyDetails } from './pages/public/PropertyDetails'
import { Login } from './pages/auth/Login'
import { Dashboard } from './pages/admin/Dashboard'
import { PropertyManagement } from './pages/admin/PropertyManagement'
import { Clients } from './pages/admin/Clients'
import { ClientDetailPage } from './pages/admin/ClientDetail'
import { Owners } from './pages/admin/Owners'
import { OwnerDetailPage } from './pages/admin/OwnerDetail'
import { BankReturnsPage } from '@/pages/admin/BankReturns'

function App() {
  return (
    <Routes>
      {/* Rotas Públicas */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="imoveis" element={<Properties />} />
        <Route path="imoveis/:id" element={<PropertyDetails />} />
        <Route path="login" element={<Login />} />
      </Route>

      {/* Rotas Administrativas */}
      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="imoveis" element={<PropertyManagement />} />
        <Route path="clientes" element={<Clients />} />
        <Route path="clientes/:id" element={<ClientDetailPage />} />
        <Route path="proprietarios" element={<Owners />} />
        <Route path="proprietarios/:id" element={<OwnerDetailPage />} />
        <Route path="retornos-bancarios" element={<BankReturnsPage />} />
      </Route>
    </Routes>
  )
}

export default App 