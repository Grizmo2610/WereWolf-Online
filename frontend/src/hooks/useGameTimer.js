import { useEffect, useState } from 'react'

export function useGameTimer(durationSeconds, serverStartedAt) {
  const [remaining, setRemaining] = useState(durationSeconds || 0)

  useEffect(() => {
    if (!durationSeconds || !serverStartedAt) {
      setRemaining(0)
      return
    }

    const compute = () => {
      const elapsed = (Date.now() - new Date(serverStartedAt).getTime()) / 1000
      return Math.max(0, durationSeconds - elapsed)
    }

    setRemaining(compute())
    const interval = setInterval(() => setRemaining(compute()), 1000)
    return () => clearInterval(interval)
  }, [durationSeconds, serverStartedAt])

  return remaining
}

export function formatMMSS(seconds) {
  const total = Math.max(0, Math.round(seconds))
  const mm = String(Math.floor(total / 60)).padStart(2, '0')
  const ss = String(total % 60).padStart(2, '0')
  return `${mm}:${ss}`
}
