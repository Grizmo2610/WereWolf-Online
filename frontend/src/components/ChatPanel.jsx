import { useEffect, useRef, useState } from 'react'
import { useMentionHighlight } from '../hooks/useMentionHighlight'
import VoteCounter from './VoteCounter'

const BANNER_STYLES = {
  death: { bg: 'rgba(248,113,113,0.15)', border: 'rgba(248,113,113,0.3)', color: '#fca5a5' },
  reveal: { bg: 'rgba(248,113,113,0.15)', border: 'rgba(248,113,113,0.3)', color: '#fca5a5' },
  warn: { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.3)', color: 'var(--warning)' },
  phase: { bg: 'rgba(255,123,0,0.1)', border: 'rgba(255,123,0,0.25)', color: 'var(--accent-orange)' },
  info: { bg: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.1)', color: 'var(--text-muted)' },
  safe: { bg: 'rgba(34,197,94,0.1)', border: 'rgba(34,197,94,0.25)', color: 'var(--success)' },
  end: { bg: 'rgba(255,123,0,0.15)', border: 'rgba(255,123,0,0.35)', color: 'var(--accent-orange)' },
}

export default function ChatPanel({
  feed,
  isAlive,
  isGhost,
  ghostUsedThisRound,
  isSilenced,
  phase,
  mySeatId,
  myDisplayName,
  voteCounts,
  totalVoted,
  totalEligible,
  players,
  onSend,
}) {
  const [text, setText] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [feed])

  const canSpeakPublic = phase === 'discussion' && (isAlive || isGhost) && !isSilenced && !(isGhost && ghostUsedThisRound)
  const canSpeakDead = !isAlive

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed) return
    if (isGhost && !isAlive && trimmed.split(/\s+/).length > 1) return
    const channel = isAlive ? 'public' : 'dead'
    onSend(trimmed, channel)
    setText('')
  }

  const publicFeed = feed.filter((item) => item.type !== 'chat' || item.channel === 'public')
  const deadFeed = feed.filter((item) => item.type === 'chat' && item.channel === 'dead')

  return (
    <div className="glass-card flex flex-col h-full overflow-hidden">
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2">
        {publicFeed.map((item) => (
          <FeedItem key={item.id} item={item} mySeatId={mySeatId} myDisplayName={myDisplayName} />
        ))}

        {phase === 'vote' && (
          <VoteCounter voteCounts={voteCounts} totalVoted={totalVoted} totalEligible={totalEligible} players={players} />
        )}

        {!isAlive && (
          <>
            <div className="text-center text-xs py-2" style={{ color: 'var(--text-faintest)' }}>
              ── 💀 Chỉ người chết thấy ──
            </div>
            {deadFeed.map((item) => (
              <FeedItem key={item.id} item={item} mySeatId={mySeatId} myDisplayName={myDisplayName} />
            ))}
          </>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 p-2.5" style={{ borderTop: '1px solid var(--card-border)' }}>
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={!canSpeakPublic && !canSpeakDead}
          placeholder={
            isGhost && !isAlive && ghostUsedThisRound
              ? 'Hồn Ma đã dùng hết lượt nói hôm nay'
              : isSilenced
                ? 'Bạn đang bị im lặng hóa'
                : !isAlive
                  ? 'Nói với người đã khuất...'
                  : phase !== 'discussion'
                    ? 'Chỉ nói được trong giờ thảo luận'
                    : isGhost
                      ? 'Hồn Ma: chỉ được 1 từ mỗi ngày'
                      : 'Nhập tin nhắn...'
          }
          className="form-input"
          style={{ flex: 1 }}
        />
        <button type="submit" disabled={!canSpeakPublic && !canSpeakDead} className="btn btn-primary" style={{ width: 'auto', padding: '10px 20px' }}>
          Gửi
        </button>
      </form>
    </div>
  )
}

function FeedItem({ item, mySeatId, myDisplayName }) {
  const isMe = item.seatId === mySeatId
  const isMentioned = useMentionHighlight(item.text, mySeatId, myDisplayName) && !isMe

  if (item.type === 'banner') {
    const style = BANNER_STYLES[item.kind] || BANNER_STYLES.info
    return (
      <div
        className="text-center text-sm rounded-lg px-3 py-1.5 mx-auto max-w-[90%]"
        style={{ background: style.bg, border: `1px solid ${style.border}`, color: style.color }}
      >
        {item.text}
      </div>
    )
  }

  return (
    <div className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`rounded-xl px-3 py-2 max-w-[80%] ${isMentioned ? 'mention-pulse' : ''}`}
        style={{
          background: 'rgba(255,255,255,0.05)',
          border: isMentioned ? '2px solid var(--accent-orange)' : '1px solid rgba(255,255,255,0.08)',
          color: 'var(--text)',
        }}
      >
        <div className="text-xs font-bold mb-0.5" style={{ color: 'var(--accent-orange)' }}>
          Ghế {item.seatId} · {item.displayName}
        </div>
        <div className="text-sm">{item.text}</div>
      </div>
    </div>
  )
}
