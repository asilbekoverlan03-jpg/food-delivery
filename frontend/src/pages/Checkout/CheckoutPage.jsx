import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import { formatPrice } from '../../utils/format'
import './Checkout.css'

export default function CheckoutPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [address, setAddress] = useState(user?.delivery_address || '')
  const [cart, setCart]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/cart/').then(r => setCart(r.data)).finally(() => setLoading(false))
  }, [])

  const handleOrder = async () => {
    setError('')
    setSubmitting(true)
    try {
      const { data } = await api.post('/orders/', { delivery_address: address })
      toast.success('Заказ оформлен!')
      navigate(`/orders/${data.id}`)
    } catch (err) {
      const msg = err.response?.data?.detail || 'Ошибка оформления заказа'
      setError(msg)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="page-loader">Загрузка...</div>
  if (!cart || cart.items.length === 0) {
    navigate('/cart'); return null
  }

  return (
    <div className="page">
      <h1 className="checkout-title">Оформление заказа</h1>

      <div className="checkout-layout">
        {/* Состав */}
        <div className="checkout-items card">
          <h2>Ваш заказ</h2>
          {cart.items.map(ci => (
            <div key={ci.id} className="checkout-row">
              <span>{ci.item.name} × {ci.quantity}</span>
              <span>{formatPrice(parseFloat(ci.item.price) * ci.quantity)}</span>
            </div>
          ))}
          <div className="checkout-total">
            <strong>Итого:</strong>
            <strong>{formatPrice(cart.total_price)}</strong>
          </div>
        </div>

        {/* Форма */}
        <div className="checkout-form card">
          <h2>Адрес доставки</h2>
          <div className="form-group mt-16">
            <label>Адрес</label>
            <input
              type="text"
              value={address}
              onChange={e => setAddress(e.target.value)}
              placeholder="Улица, дом, квартира"
            />
          </div>
          {error && <p className="error-msg">{error}</p>}
          <button
            className="btn btn-primary"
            style={{ width: '100%' }}
            disabled={submitting || !address.trim()}
            onClick={handleOrder}
          >
            {submitting ? 'Оформляем...' : 'Подтвердить заказ'}
          </button>
        </div>
      </div>
    </div>
  )
}
