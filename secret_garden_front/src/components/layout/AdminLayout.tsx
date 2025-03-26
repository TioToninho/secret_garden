import { Outlet } from 'react-router-dom'
import { Sidebar } from '../Sidebar'

export function AdminLayout() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 bg-gray-50">
        <Outlet />
      </div>
    </div>
  )
} 