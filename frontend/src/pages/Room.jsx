import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useWebSocket } from '../hooks/useWebSocket'
import { useGameStore } from '../store/gameStore'
import { useAuthStore } from '../store/authStore'
import { DISCUSSION_MIN, DISCUSSION_MAX, VOTE_MIN, VOTE_MAX, NIGHT_MIN, NIGHT_MAX, EARLY_VOTE_MIN } from '../config/timingBounds'

const AVATARS = ['🐺', '🌑', '🌕', '🦉', '🕯️', '🗡️', '🌙', '🔮']

export default function Room() {
  const { roomCode } = useParams()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const { seats, hostSeatId, status, isConnected, roomSettings, setMySeatId, reset } = useGameStore()
  const { send } = useWebSocket(roomCode)
  const [copied, setCopied] = useState(false)

  const mySeat = useMemo(() => seats.find((s) => s.user_id === user?.id), [seats, user])
  const isReady = !!mySeat?.is_ready

  useEffect(() => {
    if (mySeat) setMySeatId(mySeat.seat_id)
  }, [mySeat, setMySeatId])

  useEffect(() => {
    if (status === 'in_progress') {
      navigate(`/game/${roomCode}`)
    }
  }, [status, roomCode, navigate])

  const isHost = mySeat?.seat_id === hostSeatId
  const readyCount = seats.filter((s) => s.is_ready).length
  const canStart = isHost && seats.length > 0 && readyCount === seats.length

  const copyCode = () => {
    navigator.clipboard.writeText(roomCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  const handleLeave = () => {
    send('LEAVE_ROOM')
    reset()
    navigate('/lobby')
  }

  return (
    <div className="min-h-screen px-4 py-6 flex flex-col items-center relative">
      <div className="relative z-[1] w-full max-w-[640px] flex flex-col gap-5">
        <div className="glass-card p-6">
          <div className="flex justify-between items-center mb-5 flex-wrap gap-2.5">
            <div className="inline-flex items-center gap-2.5 flex-wrap">
              <h1 className="text-lg font-extrabold" style={{ color: 'var(--text-strong)' }}>
                Mã phòng:{' '}
                <span
                  className="font-mono text-2xl font-extrabold tracking-widest"
                  style={{ color: 'var(--accent-orange)', textShadow: '0 0 12px rgba(255,123,0,0.35)' }}
                >
                  {roomCode}
                </span>
              </h1>
              <button
                onClick={copyCode}
                className="text-sm px-3 py-1.5 rounded-lg border transition-colors"
                style={{
                  background: copied ? 'rgba(34,197,94,0.12)' : 'rgba(255,255,255,0.06)',
                  borderColor: copied ? 'rgba(34,197,94,0.4)' : 'rgba(255,255,255,0.1)',
                  color: copied ? 'var(--success)' : 'var(--text-muted)',
                }}
              >
                {copied ? 'Đã chép!' : 'Sao chép'}
              </button>
            </div>
          </div>

          {!isConnected && <div className="form-error">Đang kết nối...</div>}

          <div className="flex flex-col gap-2 mb-5">
            {seats.map((seat, i) => (
              <div
                key={seat.seat_id}
                className="flex items-center justify-between p-3.5 rounded-xl transition-transform"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <div className="flex items-center gap-2.5">
                  <div className="avatar-circle w-8.5 h-8.5 text-base">{AVATARS[i % AVATARS.length]}</div>
                  <span className="font-bold text-sm" style={{ color: 'var(--text-strong)' }}>
                    Ghế {seat.seat_id} — {seat.display_name}
                    {seat.seat_id === hostSeatId && (
                      <span className="ml-1" style={{ filter: 'drop-shadow(0 0 4px rgba(251,191,36,0.45))' }}>
                        👑
                      </span>
                    )}
                  </span>
                </div>
                <span className={`status-pill ${seat.is_ready ? 'ready' : 'waiting'}`}>
                  <span className={`status-dot ${seat.is_ready ? 'ready-dot' : 'waiting-dot'}`} />
                  {seat.is_ready ? 'Sẵn sàng' : 'Chờ...'}
                </span>
              </div>
            ))}
          </div>

          <div className="flex gap-2.5 flex-wrap mb-2.5">
            <button onClick={() => send(isReady ? 'UNREADY' : 'READY')} className="btn btn-accent" style={{ flex: '1 1 auto' }}>
              {isReady ? 'Hủy sẵn sàng' : 'Sẵn sàng'}
            </button>
            {isHost && (
              <button
                onClick={() => send('START_GAME')}
                disabled={!canStart}
                className="btn btn-primary"
                style={{ flex: '1 1 auto' }}
              >
                Bắt đầu
              </button>
            )}
          </div>
          <button onClick={handleLeave} className="btn btn-danger-outline">
            Thoát phòng
          </button>
          <p className="text-center text-sm mt-2.5 font-semibold" style={{ color: 'var(--text-faint)' }}>
            Sẵn sàng: {readyCount}/{seats.length}
          </p>
        </div>

        <RoomSettingsPanel isHost={isHost} settings={roomSettings} onChange={(s) => send('UPDATE_ROOM_SETTINGS', s)} />
      </div>
    </div>
  )
}

function RoomSettingsPanel({ isHost, settings, onChange }) {
  const [draft, setDraft] = useState(settings)

  useEffect(() => {
    setDraft(settings)
  }, [settings])

  if (!settings || !draft) return null

  const fields = [
    { key: 'discussion_seconds', label: 'Thời gian thảo luận (giây)', min: DISCUSSION_MIN, max: DISCUSSION_MAX },
    { key: 'early_vote_after_seconds', label: 'Cho vote sớm sau (giây)', min: EARLY_VOTE_MIN, max: DISCUSSION_MAX },
    { key: 'vote_seconds', label: 'Thời gian bỏ phiếu (giây)', min: VOTE_MIN, max: VOTE_MAX },
    { key: 'night_seconds', label: 'Thời gian ban đêm (giây)', min: NIGHT_MIN, max: NIGHT_MAX },
  ]

  const isDirty = JSON.stringify(draft) !== JSON.stringify(settings)

  return (
    <div className="glass-card p-6">
      <h2 className="text-lg font-extrabold mb-4" style={{ color: 'var(--text-strong)' }}>
        Tùy chọn ván đấu {!isHost && <span className="text-xs font-normal" style={{ color: 'var(--text-faint)' }}>(chỉ chủ phòng chỉnh được)</span>}
      </h2>

      <label className="toggle-row mb-3">
        <input
          type="checkbox"
          disabled={!isHost}
          checked={draft.reveal_on_death}
          onChange={(e) => setDraft({ ...draft, reveal_on_death: e.target.checked })}
        />
        <span>Lộ role khi chết</span>
      </label>

      <div className="grid gap-3.5 sm:grid-cols-2 mt-2.5">
        {fields.map((f) => (
          <div key={f.key}>
            <label className="form-label">{f.label}</label>
            <input
              type="number"
              min={f.min}
              max={f.max}
              step={5}
              disabled={!isHost}
              value={draft[f.key]}
              onChange={(e) => setDraft({ ...draft, [f.key]: e.target.value === '' ? '' : Number(e.target.value) })}
              onBlur={(e) => {
                const clamped = Math.min(f.max, Math.max(f.min, Number(e.target.value) || f.min))
                setDraft({ ...draft, [f.key]: clamped })
              }}
              className="form-input"
            />
          </div>
        ))}
      </div>

      {isHost && (
        <button onClick={() => onChange(draft)} disabled={!isDirty} className="btn btn-primary mt-5">
          Lưu tùy chọn
        </button>
      )}
    </div>
  )
}
