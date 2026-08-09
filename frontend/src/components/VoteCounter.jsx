export default function VoteCounter({ voteCounts, totalVoted, totalEligible }) {
  const entries = Object.entries(voteCounts).sort((a, b) => b[1] - a[1])
  const maxVotes = entries.length ? entries[0][1] : 1

  return (
    <div className="rounded-xl p-3 my-2" style={{ background: 'rgba(255,123,0,0.06)', border: '1px solid rgba(255,123,0,0.2)' }}>
      <p className="font-bold mb-2" style={{ color: 'var(--text-strong)' }}>
        ⚖️ Đang bỏ phiếu... ({totalVoted}/{totalEligible} đã vote)
      </p>
      {entries.length === 0 && (
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Chưa có phiếu nào.
        </p>
      )}
      {entries.map(([seatId, count]) => (
        <div key={seatId} className="flex items-center gap-2 text-sm mb-1">
          <span className="w-16 shrink-0" style={{ color: 'var(--text-muted)' }}>
            Ghế {seatId}
          </span>
          <div className="flex-1 h-3 rounded-full overflow-hidden" style={{ background: 'var(--input-bg)' }}>
            <div
              className="h-full"
              style={{ width: `${(count / maxVotes) * 100}%`, background: 'linear-gradient(90deg, var(--accent-red), var(--accent-orange))' }}
            />
          </div>
          <span className="w-10 text-right font-semibold" style={{ color: 'var(--text-strong)' }}>
            {count}
          </span>
        </div>
      ))}
    </div>
  )
}
