import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { APP_NAME } from '../config'
import './Navbar.css'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">🍔 {APP_NAME}</Link>
      <div className="navbar-links">
        <Link to="/">Рестораны</Link>
        {user ? (
          <>
            <Link to="/cart">🛒 Корзина</Link>
            <Link to="/orders">Мои заказы</Link>
            <Link to="/profile">👤 {user.username}</Link>
            <button onClick={handleLogout} className="btn-logout">Выйти</button>
          </>
        ) : (
          <>
            <Link to="/login">Войти</Link>
            <Link to="/register" className="btn-primary-link">Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  )
}
