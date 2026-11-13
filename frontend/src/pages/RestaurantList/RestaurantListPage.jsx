import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import api from '../../api/axios'
import toast from 'react-hot-toast'
import { formatPrice } from '../../utils/format'
import './RestaurantList.css'

/** Строим полный URL для изображения (логотип, фото, аватар). */
export function buildImageUrl(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  return `http://127.0.0.1:8003${path}`
}

function Stars({ value }) {
  return (
    <span className="stars-display">
      {'★'.repeat(Math.round(value))}{'☆'.repeat(5 - Math.round(value))}
      <span className="stars-val"> {value}</span>
    </span>
  )
}

export default function RestaurantListPage() {
  const [restaurants, setRestaurants] = useState([])
  const [loading, setLoading]   = useState(true)
  const [search, setSearch]     = useState('')
  const [openOnly, setOpenOnly] = useState(false)
  const [ordering, setOrdering] = useState('')
  const [page, setPage]         = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = { page }
      if (search)   params.search = search
      if (openOnly) params.is_open = true
      if (ordering) params.ordering = ordering
      const { data } = await api.get('/restaurants/', { params })
      setRestaurants(data.results ?? data)
      if (data.count) setTotalPages(Math.ceil(data.count / 10))
    } catch {
      toast.error('Ошибка загрузки ресторанов')
    } finally {
      setLoading(false)
    }
  }, [search, openOnly, ordering, page])

  useEffect(() => { fetchData() }, [fetchData])
  useEffect(() => { setPage(1) }, [search, openOnly, ordering])

  return (
    <div className="page">
      <h1 className="page-heading">Рестораны</h1>

      {/* Фильтры */}
      <div className="filters">
        <input
          className="search-input"
          placeholder="Поиск по названию..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <label className="checkbox-label">
          <input type="checkbox" checked={openOnly} onChange={e => setOpenOnly(e.target.checked)} />
          Только открытые
        </label>
        <select value={ordering} onChange={e => setOrdering(e.target.value)} className="select-sort">
          <option value="">Без сортировки</option>
          <option value="delivery_time">По времени доставки</option>
          <option value="min_order_price">По мин. сумме</option>
          <option value="-delivery_time">По времени (убыв.)</option>
        </select>
      </div>

      {loading && <div className="page-loader">Загрузка...</div>}

      {!loading && restaurants.length === 0 && (
        <p className="text-muted text-center mt-24">Ничего не найдено</p>
      )}

      <div className="grid-3 mt-16">
        {restaurants.map(r => (
          <Link to={`/restaurants/${r.id}`} key={r.id} className="restaurant-card card">
            <div className="restaurant-img-wrap">
              {r.logo
                ? <img src={buildImageUrl(r.logo)} alt={r.name} className="restaurant-img" />
                : <div className="restaurant-img-placeholder">🍽️</div>
              }
              {!r.is_open && <span className="badge-closed">Закрыто</span>}
            </div>
            <div className="restaurant-info">
              <h2>{r.name}</h2>
              <p className="text-muted">{r.address}</p>
              <div className="restaurant-meta">
                <Stars value={r.avg_rating} />
                <span>⏱ {r.delivery_time} мин</span>
                <span>от {formatPrice(r.min_order_price)}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Пагинация */}
      {totalPages > 1 && (
        <div className="pagination">
          <button className="btn btn-secondary btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>←</button>
          <span>{page} / {totalPages}</span>
          <button className="btn btn-secondary btn-sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>→</button>
        </div>
      )}
    </div>
  )
}
