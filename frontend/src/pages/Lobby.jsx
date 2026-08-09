import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '../api/client'
import { useAuthStore } from '../store/authStore'

export default function Lobby() {
  const [scenarios, setScenarios] = useState([])
  const [scenarioId, setScenarioId] = useState('classic')
  const [joinCode, setJoinCode] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  useEffect(() => {
    api.listScenarios().then(setScenarios).catch(() => setScenarios([]))
  }, [])

  const handleCreate = async () => {
    setError('')
    try {
      const res = await api.createRoom(scenarioId)
      navigate(`/room/${res.room_code}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Không tạo được phòng')
    }
  }

  const handleJoin = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.joinRoom(joinCode.trim().toUpperCase())
      navigate(`/room/${res.room_code}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Không vào được phòng')
    }
  }

  return (
    <div className="min-h-screen px-4 py-6 flex flex-col items-center relative">
      <div className="relative z-[1] w-full max-w-[480px] flex flex-col gap-4.5">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-3">
            <div className="avatar-circle w-11 h-11 text-2xl">🐺</div>
            <h1 className="text-xl font-extrabold" style={{ color: 'var(--text-strong)' }}>
              Xin chào, {user?.display_name}
            </h1>
          </div>
          <button
            onClick={logout}
            className="text-sm font-semibold px-2.5 py-1.5 rounded-lg transition-colors"
            style={{ color: 'var(--text-muted)' }}
          >
            Đăng xuất
          </button>
        </div>

        {error && <div className="form-error">{error}</div>}

        <div className="glass-card p-6">
          <h2 className="gradient-text text-lg mb-3.5">Tạo phòng mới</h2>
          <label className="form-label" htmlFor="mode">
            Chế độ chơi
          </label>
          <select
            id="mode"
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="form-input mb-3"
          >
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.min_players}-{s.max_players} người)
              </option>
            ))}
          </select>
          <button onClick={handleCreate} className="btn btn-primary">
            Tạo phòng
          </button>
        </div>

        <div className="glass-card p-6">
          <h2 className="gradient-text text-lg mb-3.5">Vào phòng có sẵn</h2>
          <form onSubmit={handleJoin} className="flex gap-2.5">
            <input
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value)}
              placeholder="Mã phòng"
              className="form-input uppercase"
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn btn-accent" style={{ width: 'auto', padding: '10px 24px' }}>
              Vào
            </button>
          </form>
          <span className="form-hint">Nhập mã phòng do bạn bè gửi để tham gia.</span>
        </div>
      </div>
    </div>
  )
}
