import { useEffect, useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import toast from 'react-hot-toast'
import { buildImageUrl } from '../RestaurantList/RestaurantListPage'
import { formatPrice } from '../../utils/format'
import './Cart.css'

export default function CartPage() {
  const navigate = useNavigate()
  const [cart, setCart]         = useState(null)
  const [loading, setLoading]   = useState(true)
  const [minOrder, setMinOrder] = useState(0)

  const fetchCart = useCallback(async () => {
    try {
      const { data } = await api.get('/cart/')
      setCart(data)
      if (data.items.length > 0) {
        try {
          const rId = data.items[0].item.category
          const catData = await api.get(`/categories/${rId}/`)
          const rData = await api.get(`/restaurants/${catData.data.restaurant}/`)
          setMinOrder(parseFloat(rData.data.min_order_price))
        } catch { /* не критично */ }
      }
    } catch {
      toast.error('Ошибка загрузки корзины')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchCart() }, [fetchCart])

  const updateQty = async (itemId, qty) => {
    if (qty < 1) return removeItem(itemId)
    try {
      const { data } = await api.patch(`/cart/items/${itemId}/`, { quantity: qty })
      setCart(data)
    } catch { toast.error('Ошибка обновления') }
  }

  const removeItem = async (itemId) => {
    try {
      await api.delete(`/cart/items/${itemId}/`)
      setCart(prev => ({
        ...prev,
        items: prev.items.filter(i => i.id !== itemId),
        total_price: prev.items
          .filter(i => i.id !== itemId)
          .reduce((s, i) => s + parseFloat(i.item.price) * i.quantity, 0),
      }))
    } catch { toast.error('Ошибка удаления') }
  }

  const clearCart = async () => {
    try {
      await api.delete('/cart/clear/')
      setCart(prev => ({ ...prev, items: [], total_price: 0 }))
      toast.success('Корзина очищена')
    } catch { toast.error('Ошибка') }
  }

  if (loading) return <div className="page-loader">Загрузка...</div>
  if (!cart || cart.items.length === 0) return (
    <div className="page text-center">
      <p style={{ fontSize: '3rem' }}>🛒</p>
      <h2>Корзина пуста</h2>
      <p className="text-muted mt-8">Добавьте блюда из <Link to="/" style={{ color: 'var(--accent)' }}>списка ресторанов</Link></p>
    </div>
  )

  const total = parseFloat(cart.total_price)
  const tooLow = minOrder > 0 && total < minOrder

  return (
    <div className="page">
      <div className="cart-header">
        <h1>Корзина</h1>
        <button className="btn btn-secondary btn-sm" onClick={clearCart}>Очистить</button>
      </div>

      <div className="cart-layout">
        <div className="cart-items">
          {cart.items.map(ci => (
            <div key={ci.id} className="cart-item card">
              {ci.item.photo && (
                <img src={buildImageUrl(ci.item.photo)} alt={ci.item.name} className="cart-item-img" />
              )}
              <div className="cart-item-info">
                <h3>{ci.item.name}</h3>
                <p className="text-muted">{formatPrice(ci.item.price)} × {ci.quantity}</p>
              </div>
              <div className="cart-item-controls">
                <button className="btn btn-secondary btn-sm" onClick={() => updateQty(ci.id, ci.quantity - 1)}>−</button>
                <span className="qty">{ci.quantity}</span>
                <button className="btn btn-secondary btn-sm" onClick={() => updateQty(ci.id, ci.quantity + 1)}>+</button>
                <button className="btn btn-danger btn-sm" onClick={() => removeItem(ci.id)}>✕</button>
              </div>
              <div className="cart-item-sum">
                {formatPrice(parseFloat(ci.item.price) * ci.quantity)}
              </div>
            </div>
          ))}
        </div>

        <div className="cart-summary card">
          <h2>Итого</h2>
          <div className="summary-row">
            <span>Сумма</span>
            <strong>{formatPrice(total)}</strong>
          </div>
          {tooLow && (
            <p className="warning-msg">
              ⚠️ Минимальная сумма заказа {formatPrice(minOrder)}. Не хватает {formatPrice(minOrder - total)}
            </p>
          )}
          <button
            className="btn btn-primary"
            style={{ width: '100%', marginTop: 16 }}
            disabled={tooLow}
            onClick={() => navigate('/checkout')}
          >
            Оформить заказ
          </button>
        </div>
      </div>
    </div>
  )
}
