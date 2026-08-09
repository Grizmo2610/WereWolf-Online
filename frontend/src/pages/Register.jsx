import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { ApiError } from '../api/client'

export default function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const register = useAuthStore((s) => s.register)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(username, password, displayName)
      navigate('/lobby')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Đăng ký thất bại')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative">
      <div className="moon-glow" />

      <form onSubmit={handleSubmit} className="glass-card w-full max-w-[400px] p-9 px-7">
        <div className="flex justify-center mb-2.5">
          <div className="logo-circle">🐺</div>
        </div>
        <h1 className="gradient-text text-center text-2xl mb-7">Tạo tài khoản</h1>

        {error && <div className="form-error">{error}</div>}

        <div className="mb-4">
          <label className="form-label" htmlFor="username">
            Tên đăng nhập
          </label>
          <input
            id="username"
            name="username"
            type="text"
            className="form-input"
            placeholder="wolf_hunter_99"
            minLength={3}
            maxLength={20}
            pattern="^[a-zA-Z0-9_]+$"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <span className="form-hint">3-20 ký tự, chỉ dùng chữ, số và dấu gạch dưới.</span>
        </div>

        <div className="mb-4">
          <label className="form-label" htmlFor="displayName">
            Tên hiển thị
          </label>
          <input
            id="displayName"
            name="displayName"
            type="text"
            className="form-input"
            placeholder="Bóng ma đêm"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
          <span className="form-hint">Bỏ trống nếu muốn dùng tên đăng nhập.</span>
        </div>

        <div className="mb-6">
          <label className="form-label" htmlFor="password">
            Mật khẩu
          </label>
          <input
            id="password"
            name="password"
            type="password"
            className="form-input"
            placeholder="••••••"
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <span className="form-hint">Tối thiểu 6 ký tự. Khuyến nghị kết hợp chữ và số.</span>
        </div>

        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? 'Đang tạo...' : 'Đăng ký'}
        </button>

        <p className="text-center text-sm mt-4.5" style={{ color: 'var(--text-faint)' }}>
          Đã có tài khoản?{' '}
          <Link to="/login" className="link">
            Đăng nhập
          </Link>
        </p>
      </form>
    </div>
  )
}
