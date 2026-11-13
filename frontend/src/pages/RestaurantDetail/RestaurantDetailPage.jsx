import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../../api/axios'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import { buildImageUrl } from '../RestaurantList/RestaurantListPage'
import { formatPrice } from '../../utils/format'
import './RestaurantDetail.css'

/** Компонент выбора звёзд */
function StarPicker({ value, onChange }) {
  return (
    <div className="stars-input">
      {[1,2,3,4,5].map(s => (
        <button
          key={s} type="button"
          className={`star-btn ${s <= value ? 'active' : ''}`}
          onClick={() => onChange(s)}
        >★</button>
      ))}
    </div>
  )
}

export default function RestaurantDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()

  const [restaurant, setRestaurant] = useState(null)
  const [reviews, setReviews]       = useState([])
  const [loading, setLoading]       = useState(true)
  const [addingItem, setAddingItem] = useState(null) // id блюда в процессе добавления

  // форма отзыва
  const [reviewForm, setReviewForm] = useState({ stars: 5, comment: '' })
  const [reviewLoading, setReviewLoading] = useState(false)
  const [reviewError, setReviewError]     = useState('')

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [rRes, revRes] = await Promise.all([
          api.get(`/restaurants/${id}/`),
          api.get(`/restaurants/${id}/reviews/`),
        ])
        setRestaurant(rRes.data)
        setReviews(revRes.data)
      } catch {
        toast.error('Ошибка загрузки ресторана')
      } finally {
        setLoading(false)
      }
    }
    fetchAll()
  }, [id])

  const handleAddToCart = async (itemId) => {
    if (!user) { toast.error('Войдите, чтобы добавить в корзину'); return }
    setAddingItem(itemId)
    try {
      await api.post('/cart/items/', { item_id: itemId, quantity: 1 })
      toast.success('Добавлено в корзину')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Ошибка добавления')
    } finally {
      setAddingItem(null)
    }
  }

  const handleReviewSubmit = async (e) => {
    e.preventDefault()
    setReviewError('')
    setReviewLoading(true)
    try {
      const { data } = await api.post(`/restaurants/${id}/reviews/`, reviewForm)
      setReviews(prev => [data, ...prev])
      setReviewForm({ stars: 5, comment: '' })
      toast.success('Отзыв опубликован!')
    } catch (err) {
      const msg = err.response?.data?.detail || JSON.stringify(err.response?.data)
      setReviewError(msg || 'Ошибка')
    } finally {
      setReviewLoading(false)
    }
  }

  if (loading) return <div className="page-loader">Загрузка...</div>
  if (!restaurant) return <p className="text-muted text-center mt-24">Ресторан не найден</p>

  const userHasReview = reviews.some(r => r.username === user?.username)

  return (
    <div className="page">
      {/* Шапка ресторана */}
      <div className="restaurant-header card">
        {restaurant.logo && (
          <img src={buildImageUrl(restaurant.logo)} alt={restaurant.name} className="rest-header-img" />
        )}
        <div className="rest-header-info">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <h1>{restaurant.name}</h1>
            {!restaurant.is_open && <span className="badge badge-new">Закрыто</span>}
          </div>
          <p className="text-muted">{restaurant.address}</p>
          <p style={{ marginTop: 8 }}>{restaurant.description}</p>
          <div className="rest-header-meta">
            <span>⭐ {restaurant.avg_rating} ({restaurant.reviews_count} отзывов)</span>
            <span>⏱ {restaurant.delivery_time} мин</span>
            <span>от {formatPrice(restaurant.min_order_price)}</span>
          </div>
        </div>
      </div>

      {/* Меню по категориям */}
      <h2 className="section-title">Меню</h2>
      {restaurant.categories.length === 0 && (
        <p className="text-muted">Меню пока не добавлено</p>
      )}
      {restaurant.categories.map(cat => (
        <div key={cat.id} className="menu-category">
          <h3 className="category-name">{cat.name}</h3>
          <div className="grid-3">
            {cat.items.map(item => (
              <div key={item.id} className={`menu-item card ${!item.is_available ? 'unavailable' : ''}`}>
                {item.photo && (
                  <img src={buildImageUrl(item.photo)} alt={item.name} className="menu-item-img" />
                )}
                <div className="menu-item-body">
                  <h4>{item.name}</h4>
                  <p className="text-muted">{item.description}</p>
                  {item.weight > 0 && <p className="text-muted">{item.weight} г</p>}
                  <div className="menu-item-footer">
                    <span className="menu-item-price">{formatPrice(item.price)}</span>
                    <button
                      className="btn btn-primary btn-sm"
                      disabled={!item.is_available || addingItem === item.id}
                      onClick={() => handleAddToCart(item.id)}
                    >
                      {!item.is_available ? 'Недоступно' : addingItem === item.id ? '...' : '+ В корзину'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Отзывы */}
      <h2 className="section-title">Отзывы</h2>

      {/* Форма отзыва */}
      {user && !userHasReview && (
        <div className="review-form card">
          <h3>Оставить отзыв</h3>
          <form onSubmit={handleReviewSubmit}>
            <div className="form-group mt-16">
              <label>Оценка</label>
              <StarPicker value={reviewForm.stars} onChange={s => setReviewForm(f => ({ ...f, stars: s }))} />
            </div>
            <div className="form-group">
              <label>Комментарий</label>
              <textarea
                rows={3}
                value={reviewForm.comment}
                onChange={e => setReviewForm(f => ({ ...f, comment: e.target.value }))}
              />
            </div>
            {reviewError && <p className="error-msg">{reviewError}</p>}
            <button className="btn btn-primary" disabled={reviewLoading}>
              {reviewLoading ? 'Отправляем...' : 'Опубликовать'}
            </button>
          </form>
        </div>
      )}
      {user && userHasReview && (
        <p className="text-muted mt-8">Вы уже оставили отзыв на этот ресторан.</p>
      )}
      {!user && (
        <p className="text-muted mt-8">Войдите, чтобы оставить отзыв.</p>
      )}

      {reviews.length === 0
        ? <p className="text-muted mt-16">Отзывов пока нет. Будьте первым!</p>
        : reviews.map(rev => (
            <div key={rev.id} className="review-card card">
              <div className="review-header">
                <strong>{rev.username}</strong>
                <span className="review-stars">{'★'.repeat(rev.stars)}{'☆'.repeat(5 - rev.stars)}</span>
                <span className="text-muted">{new Date(rev.created_date).toLocaleDateString('ru')}</span>
              </div>
              {rev.comment && <p className="review-comment">{rev.comment}</p>}
            </div>
          ))
      }
    </div>
  )
}
