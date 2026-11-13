import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import './Auth.css'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '', email: '', password: '', password2: '',
    phone_number: '', delivery_address: '',
  })
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState({})

  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrors({})
    setLoading(true)
    try {
      await register(form)
      toast.success('Аккаунт создан!')
      navigate('/')
    } catch (err) {
      const data = err.response?.data || {}
      if (typeof data === 'object') setErrors(data)
      else setErrors({ non_field_errors: ['Ошибка регистрации'] })
    } finally {
      setLoading(false)
    }
  }

  const field = (name, label, type = 'text', required = false) => (
    <div className="form-group">
      <label>{label}{required && ' *'}</label>
      <input
        type={type}
        value={form[name]}
        onChange={e => setForm({ ...form, [name]: e.target.value })}
        required={required}
      />
      {errors[name] && <p className="error-msg">{errors[name].join(' ')}</p>}
    </div>
  )

  return (
    <div className="auth-page">
      <div className="auth-card card">
        <h1 className="auth-title">Регистрация</h1>
        <form onSubmit={handleSubmit}>
          {field('username', 'Логин', 'text', true)}
          {field('email', 'Email', 'email')}
          {field('password', 'Пароль', 'password', true)}
          {field('password2', 'Повторите пароль', 'password', true)}
          {field('phone_number', 'Телефон')}
          {field('delivery_address', 'Адрес доставки')}
          {errors.non_field_errors && (
            <p className="error-msg">{errors.non_field_errors.join(' ')}</p>
          )}
          <button className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Создаём...' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="auth-switch">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}
