import { useState } from 'react'
import { formatMMSS, useGameTimer } from '../hooks/useGameTimer'

const STORAGE_KEY = 'masoi_timer_mode'

export default function Timer({ durationSeconds, serverStartedAt }) {
  const remaining = useGameTimer(durationSeconds, serverStartedAt)
  const [mode, setMode] = useState(() => localStorage.getItem(STORAGE_KEY) || 'clock')

  const toggleMode = () => {
    const next = mode === 'clock' ? 'progress' : 'clock'
    setMode(next)
    localStorage.setItem(STORAGE_KEY, next)
  }

  const percent = durationSeconds ? Math.max(0, Math.min(100, (remaining / durationSeconds) * 100)) : 0
  const barColor = percent > 50 ? 'var(--accent-orange)' : percent > 20 ? 'var(--warning)' : 'var(--danger)'

  return (
    <button type="button" onClick={toggleMode} className="flex items-center gap-2 select-none" title="Bấm để đổi kiểu hiển thị">
      {mode === 'clock' ? (
        <span className="text-2xl font-extrabold tabular-nums" style={{ color: 'var(--text-strong)' }}>
          {formatMMSS(remaining)}
        </span>
      ) : (
        <div className="w-32 h-3 rounded-full overflow-hidden" style={{ background: 'var(--input-bg)', border: '1px solid var(--input-border)' }}>
          <div
            className="h-full transition-all duration-1000 ease-linear"
            style={{ width: `${percent}%`, backgroundColor: barColor }}
          />
        </div>
      )}
    </button>
  )
}
