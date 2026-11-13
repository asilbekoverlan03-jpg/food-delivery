import { useState } from 'react'
import api from '../../api/axios'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'
import { buildImageUrl } from '../RestaurantList/RestaurantListPage'
import './Profile.css'

export default function ProfilePage() {
  const { user, updateUser } = useAuth()
  const [form, setForm] = useState({
    email:            user?.email || '',
    phone_number:     user?.phone_number || '',
    delivery_address: user?.delivery_address || '',
  })
  const [avatar, setAvatar]       = useState(null)
  const [preview, setPreview]     = useState(null)
  const [loading, setLoading]     = useState(false)

  const handleAvatarChange = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setAvatar(file)
    setPreview(URL.createObjectURL(file))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('email', form.email)
      fd.append('phone_number', form.phone_number)
      fd.append('delivery_address', form.delivery_address)
      if (avatar) fd.append('avatar', avatar)

      const { data } = await api.patch('/auth/me/', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      updateUser(data)
      toast.success('Профиль сохранён')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Ошибка сохранения')
    } finally {
      setLoading(false)
    }
  }

  const avatarSrc = preview || buildImageUrl(user?.avatar)

  return (
    <div className="page">
      <h1 className="profile-title">Профиль</h1>
      <div className="profile-card card">
        {/* Аватар */}
        <div className="avatar-section">
          <div className="avatar-wrap">
            {avatarSrc
              ? <img src={avatarSrc} alt="avatar" className="avatar-img" />
              : <div className="avatar-placeholder">👤</div>
            }
          </div>
          <label className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
            Сменить фото
            <input type="file" accept="image/*" hidden onChange={handleAvatarChange} />
          </label>
        </div>

        <form onSubmit={handleSubmit} className="profile-form">
          <div className="form-group">
            <label>Логин</label>
            <input type="text" value={user?.username} disabled />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Телефон</label>
            <input type="tel" value={form.phone_number}
              onChange={e => setForm({ ...form, phone_number: e.target.value })} />
          </div>
          <div className="form-group">
            <label>Адрес доставки</label>
            <input type="text" value={form.delivery_address}
              onChange={e => setForm({ ...form, delivery_address: e.target.value })} />
          </div>
          <button className="btn btn-primary" disabled={loading}>
            {loading ? 'Сохраняем...' : 'Сохранить'}
          </button>
        </form>
      </div>
    </div>
  )
}
