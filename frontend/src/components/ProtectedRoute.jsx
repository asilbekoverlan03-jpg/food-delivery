import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

/** Оборачивает приватные страницы — редиректит на /login если не авторизован */
export default function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="page-loader">Загрузка...</div>
  if (!user) return <Navigate to="/login" replace />
  return children
}
