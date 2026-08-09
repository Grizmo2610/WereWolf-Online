import { motion } from 'framer-motion'

export default function SeatCircle({ players, mySeatId, wolfSeatIds, selectable, selectedSeat, onSelectSeat }) {
  const seatIds = Object.keys(players)
    .map(Number)
    .sort((a, b) => a - b)
  const count = seatIds.length || 1
  const radius = 42

  return (
    <div className="relative aspect-square w-full max-w-[380px] mx-auto">
      <div
        className="absolute rounded-full opacity-40"
        style={{ inset: '12%', border: '2px solid var(--input-border)' }}
      />
      {seatIds.map((seatId, i) => {
        const angle = (i / count) * 2 * Math.PI - Math.PI / 2
        const x = 50 + radius * Math.cos(angle)
        const y = 50 + radius * Math.sin(angle)
        const player = players[seatId]
        const isMe = seatId === mySeatId
        const isWolfAlly = wolfSeatIds?.includes(seatId)
        const isSelected = selectedSeat === seatId
        const canClick = selectable && player.is_alive && !isMe

        return (
          <motion.button
            key={seatId}
            type="button"
            disabled={!canClick}
            onClick={() => canClick && onSelectSeat?.(seatId)}
            className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-1"
            style={{ left: `${x}%`, top: `${y}%` }}
            animate={
              player.is_alive
                ? { opacity: 1, filter: 'grayscale(0%)', scale: isSelected ? 1.12 : 1 }
                : { opacity: 0.4, filter: 'grayscale(100%)', scale: 0.95 }
            }
            transition={{ duration: 0.8 }}
          >
            <div
              className="avatar-circle w-13 h-13 sm:w-14 sm:h-14 font-bold shadow-lg"
              style={{
                background: isWolfAlly
                  ? 'linear-gradient(135deg, var(--accent-red), #7a1f1f)'
                  : 'linear-gradient(135deg, #2a2d3e, #141E30)',
                color: isWolfAlly ? '#fff' : 'var(--text-strong)',
                borderColor: isSelected ? 'var(--accent-orange)' : isMe ? 'var(--accent-red)' : 'rgba(255,255,255,0.1)',
                borderWidth: isSelected || isMe ? 3 : 1,
                cursor: canClick ? 'pointer' : 'default',
                boxShadow: isSelected ? '0 0 16px rgba(255,123,0,0.5)' : undefined,
              }}
            >
              {seatId}
            </div>
            <span
              className="text-xs max-w-[64px] truncate"
              style={{ color: 'var(--text-muted)' }}
              title={player.display_name}
            >
              {player.display_name}
            </span>
          </motion.button>
        )
      })}
    </div>
  )
}
