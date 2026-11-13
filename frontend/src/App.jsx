import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

import RestaurantListPage  from './pages/RestaurantList/RestaurantListPage'
import RestaurantDetailPage from './pages/RestaurantDetail/RestaurantDetailPage'
import LoginPage           from './pages/Auth/LoginPage'
import RegisterPage        from './pages/Auth/RegisterPage'
import CartPage            from './pages/Cart/CartPage'
import CheckoutPage        from './pages/Checkout/CheckoutPage'
import OrdersPage          from './pages/Orders/OrdersPage'
import OrderDetailPage     from './pages/OrderDetail/OrderDetailPage'
import ProfilePage         from './pages/Profile/ProfilePage'

export default function App() {
  return (
    <AuthProvider>
      <Navbar />
      <div className="container">
        <Routes>
          {/* публичные */}
          <Route path="/"              element={<RestaurantListPage />} />
          <Route path="/restaurants/:id" element={<RestaurantDetailPage />} />
          <Route path="/login"         element={<LoginPage />} />
          <Route path="/register"      element={<RegisterPage />} />

          {/* приватные */}
          <Route path="/cart"    element={<ProtectedRoute><CartPage /></ProtectedRoute>} />
          <Route path="/checkout" element={<ProtectedRoute><CheckoutPage /></ProtectedRoute>} />
          <Route path="/orders"  element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
          <Route path="/orders/:id" element={<ProtectedRoute><OrderDetailPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        </Routes>
      </div>
    </AuthProvider>
  )
}
