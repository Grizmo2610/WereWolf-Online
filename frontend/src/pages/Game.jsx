import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useWebSocket } from '../hooks/useWebSocket'
import { useGameStore } from '../store/gameStore'
import { useAuthStore } from '../store/authStore'
import SeatCircle from '../components/SeatCircle'
import ChatPanel from '../components/ChatPanel'
import NightActionPanel from '../components/NightActionPanel'
import RoleCard from '../components/RoleCard'
import PhaseOverlay from '../components/PhaseOverlay'
import Timer from '../components/Timer'

const PHASE_NAMES = { night: 'Đêm', discussion: 'Thảo luận', vote: 'Bỏ phiếu', morning: 'Buổi sáng', ended: 'Kết thúc' }

export default function Game() {
  const { roomCode } = useParams()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const store = useGameStore()
  const { send } = useWebSocket(roomCode)

  const [selectedSeat, setSelectedSeat] = useState(null)
  const [selectedSeat2, setSelectedSeat2] = useState(null)
  const [showRoleReveal, setShowRoleReveal] = useState(true)

  const mySeatId = store.mySeatId
  const myPlayer = mySeatId != null ? store.players[mySeatId] : null
  const isAlive = myPlayer ? myPlayer.is_alive : true
  const isGhost = store.myRole?.roleId === 'ghost'
  const isSelectingForNightAction = !!store.nightActionRequest
  const isSelectingForVote = store.phase === 'vote' && isAlive

  useEffect(() => {
    setSelectedSeat(null)
    setSelectedSeat2(null)
  }, [store.phase])

  const handleSelectSeat = (seatId) => {
    if (isSelectingForNightAction && store.nightActionRequest.needs_second_target) {
      if (selectedSeat == null) setSelectedSeat(seatId)
      else if (seatId !== selectedSeat) setSelectedSeat2(seatId)
      return
    }
    setSelectedSeat(seatId)
  }

  const handleNightActionSubmit = (target, subtype, target2) => {
    send('NIGHT_ACTION', { target_seat: target, action_subtype: subtype, target_seat_2: target2 })
    setSelectedSeat(null)
    setSelectedSeat2(null)
  }

  const handleVoteSubmit = () => {
    send('VOTE', { target_seat: selectedSeat })
  }

  const handleChatSend = (text, channel) => {
    send('DAY_SPEAK', { text, channel })
  }

  if (store.winnerFaction && store.allRolesReveal) {
    return <GameEndScreen store={store} onBackToLobby={() => navigate('/lobby')} />
  }

  return (
    <div className="min-h-screen flex flex-col relative">
      <PhaseOverlay phase={store.phase} />

      {showRoleReveal && store.myRole && (
        <div className="fixed inset-0 z-20 flex items-center justify-center px-4" style={{ background: 'rgba(0,0,0,0.6)' }}>
          <div className="flex flex-col items-center gap-4">
            <RoleCard role={store.myRole} />
            <button onClick={() => setShowRoleReveal(false)} className="btn btn-primary" style={{ width: 'auto', padding: '10px 28px' }}>
              Đã rõ
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 flex flex-col lg:flex-row gap-4 p-4 max-w-6xl mx-auto w-full relative z-[1]">
        <div className="lg:w-1/2 flex flex-col items-center justify-start pt-4">
          <SeatCircle
            players={store.players}
            mySeatId={mySeatId}
            wolfSeatIds={store.wolfSeatIds}
            selectable={isSelectingForNightAction || isSelectingForVote}
            selectedSeat={selectedSeat}
            onSelectSeat={handleSelectSeat}
          />

          {isSelectingForNightAction && (
            <div className="w-full max-w-sm mt-4">
              <NightActionPanel
                request={store.nightActionRequest}
                selectedSeat={selectedSeat}
                selectedSeat2={selectedSeat2}
                onSubmit={handleNightActionSubmit}
              />
            </div>
          )}

          {isSelectingForVote && !isSelectingForNightAction && (
            <div className="w-full max-w-sm mt-4">
              <button onClick={handleVoteSubmit} className="btn" style={{ width: '100%', background: 'linear-gradient(135deg, var(--accent-red), #7a1f1f)', color: '#fff' }}>
                {selectedSeat != null ? `Vote ghế ${selectedSeat}` : 'Vote trắng'}
              </button>
            </div>
          )}

          {store.phase === 'discussion' && isAlive && (
            <button onClick={() => send('SKIP_DISCUSSION')} className="link mt-3 text-sm">
              Bỏ qua thảo luận ({store.skipCount}/{store.skipRequired || '?'})
            </button>
          )}
        </div>

        <div className="lg:w-1/2 flex-1 min-h-[400px]">
          <ChatPanel
            feed={store.feed}
            isAlive={isAlive}
            isGhost={isGhost}
            ghostUsedThisRound={myPlayer?.ghostUsedThisRound}
            isSilenced={false}
            phase={store.phase}
            mySeatId={mySeatId}
            myDisplayName={user?.display_name}
            voteCounts={store.voteCounts}
            totalVoted={store.totalVoted}
            totalEligible={store.totalEligible}
            players={store.players}
            onSend={handleChatSend}
          />
        </div>
      </div>

      <div
        className="flex items-center justify-between px-4 py-2.5 relative z-[1]"
        style={{ background: 'var(--card-bg)', backdropFilter: 'blur(16px)', borderTop: '1px solid var(--card-border)' }}
      >
        <span className="text-sm" style={{ color: 'var(--text-muted)' }}>
          {store.phase === 'lobby' ? 'Đang chuẩn bị...' : `${PHASE_NAMES[store.phase]} — Ngày/Đêm ${store.round}`}
        </span>
        <Timer durationSeconds={store.phaseDurationSeconds} serverStartedAt={store.phaseStartedAt} />
        <span className="text-sm" style={{ color: 'var(--text-muted)' }}>
          {store.myRole?.meta?.display_name_vi || ''} · Còn sống:{' '}
          {Object.values(store.players).filter((p) => p.is_alive).length}/{store.totalPlayers}
        </span>
      </div>
    </div>
  )
}

function GameEndScreen({ store, onBackToLobby }) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="glass-card w-full max-w-lg p-6 text-center">
        <h1 className="gradient-text text-2xl mb-4">
          {store.feed[store.feed.length - 1]?.text || 'Ván đấu kết thúc'}
        </h1>
        <div className="space-y-1 mb-5 text-left">
          {store.allRolesReveal.map((p) => (
            <div key={p.seat_id} className="flex justify-between text-sm py-1" style={{ color: 'var(--text)', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span>
                Ghế {p.seat_id} — {p.display_name}
              </span>
              <span className="font-bold" style={{ color: 'var(--accent-orange)' }}>
                {p.role_id}
              </span>
            </div>
          ))}
        </div>
        <button onClick={onBackToLobby} className="btn btn-primary">
          Về sảnh chờ
        </button>
      </div>
    </div>
  )
}
