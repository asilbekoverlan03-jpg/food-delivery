import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../../api/axios'
import toast from 'react-hot-toast'
import { buildImageUrl } from '../RestaurantList/RestaurantListPage'
import { formatPrice } from '../../utils/format'
import './OrderDetail.css'

const STEPS = [
  { key: 'new',       label: 'Принят' },
  { key: 'preparing', label: 'Готовится' },
  { key: 'on_way',    label: 'В пути' },
  { key: 'delivered', label: 'Доставлен' },
]

function StatusProgress({ status }) {
  const idx = STEPS.findIndex(s => s.key === status)
  return (
    <div className="status-progress">
      {STEPS.map((step, i) => (
        <div key={step.key} className={`step ${i <= idx ? 'done' : ''} ${i === idx ? 'current' : ''}`}>
          <div className="step-dot" />
          <div className="step-label">{step.label}</div>
          {i < STEPS.length - 1 && <div className="step-line" />}
        </div>
      ))}
    </div>
  )
}

export default function OrderDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [order, setOrder]     = useState(null)
  const [loading, setLoading] = useState(true)
  const intervalRef = useRef(null)

  const fetchOrder = async () => {
    try {
      const { data } = await api.get(`/orders/${id}/`)
      setOrder(data)
      if (data.status === 'delivered') clearInterval(intervalRef.current)
    } catch {
      toast.error('Ошибка загрузки заказа')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchOrder()
    // polling каждые 12 секунд
    intervalRef.current = setInterval(fetchOrder, 12000)
    return () => clearInterval(intervalRef.current)
  }, [id]) // eslint-disable-line

  const handleCancel = async () => {
    if (!confirm('Отменить заказ?')) return
    try {
      await api.delete(`/orders/${id}/`)
      toast.success('Заказ отменён')
      navigate('/orders')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Ошибка')
    }
  }

  if (loading) return <div className="page-loader">Загрузка...</div>
  if (!order)  return <p className="text-muted text-center mt-24">Заказ не найден</p>

  return (
    <div className="page">
      <div className="order-detail-header">
        <h1>Заказ #{order.id}</h1>
        <p className="text-muted">{new Date(order.created_date).toLocaleString('ru')}</p>
      </div>

      <StatusProgress status={order.status} />

      <div className="order-detail-layout">
        {/* Состав */}
        <div className="order-items card">
          <h2>Состав заказа</h2>
          {order.order_items.map(oi => (
            <div key={oi.id} className="order-detail-row">
              {oi.item.photo && (
                <img src={buildImageUrl(oi.item.photo)} alt={oi.item.name} className="oi-img" />
              )}
              <div className="oi-info">
                <span className="oi-name">{oi.item.name}</span>
                <span className="text-muted">{formatPrice(oi.price)} × {oi.quantity}</span>
              </div>
              <span className="oi-sum">{formatPrice(parseFloat(oi.price) * oi.quantity)}</span>
            </div>
          ))}
          <div className="order-total-row">
            <strong>Итого:</strong>
            <strong className="order-total-sum">{formatPrice(order.total_price)}</strong>
          </div>
        </div>

        {/* Детали */}
        <div className="order-meta card">
          <h2>Детали</h2>
          <p><b>Адрес:</b> {order.delivery_address}</p>
          <p className="mt-8"><b>Статус:</b> {STEPS.find(s => s.key === order.status)?.label}</p>
          {order.status === 'new' && (
            <button className="btn btn-danger" style={{ marginTop: 20 }} onClick={handleCancel}>
              Отменить заказ
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
