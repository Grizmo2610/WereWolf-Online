import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { ApiError } from '../api/client'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const login = useAuthStore((s) => s.login)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/lobby')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Đăng nhập thất bại')
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
        <h1 className="gradient-text text-center text-2xl mb-7">Ma Sói Online</h1>

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
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
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
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <span className="form-hint">Nhập mật khẩu tài khoản của bạn.</span>
        </div>

        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
        </button>

        <p className="text-center text-sm mt-4.5" style={{ color: 'var(--text-faint)' }}>
          Chưa có tài khoản?{' '}
          <Link to="/register" className="link">
            Đăng ký
          </Link>
        </p>
      </form>
    </div>
  )
}
