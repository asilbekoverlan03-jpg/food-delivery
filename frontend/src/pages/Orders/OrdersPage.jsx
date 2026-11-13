import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../../api/axios'
import toast from 'react-hot-toast'
import { formatPrice } from '../../utils/format'
import './Orders.css'

const STATUS_LABEL = {
  new: 'Новый',
  preparing: 'Готовится',
  on_way: 'В пути',
  delivered: 'Доставлен',
}

export default function OrdersPage() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/orders/')
      .then(r => setOrders(r.data.results ?? r.data))
      .catch(() => toast.error('Ошибка загрузки заказов'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="page-loader">Загрузка...</div>

  return (
    <div className="page">
      <h1 className="orders-title">Мои заказы</h1>
      {orders.length === 0 && (
        <p className="text-muted text-center mt-24">
          Заказов пока нет. <Link to="/" style={{ color: 'var(--accent)' }}>Заказать еду</Link>
        </p>
      )}
      {orders.map(order => (
        <Link to={`/orders/${order.id}`} key={order.id} className="order-card card">
          <div className="order-card-head">
            <span className="order-num">Заказ #{order.id}</span>
            <span className={`badge badge-${order.status}`}>{STATUS_LABEL[order.status]}</span>
          </div>
          <p className="text-muted">{new Date(order.created_date).toLocaleString('ru')}</p>
          <p className="order-addr">📍 {order.delivery_address}</p>
          <p className="order-total">{formatPrice(order.total_price)}</p>
        </Link>
      ))}
    </div>
  )
}
