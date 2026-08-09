import { useState } from 'react'

const ACTION_LABELS = {
  seer: 'Chọn người để soi phe',
  mystic_seer: 'Chọn người để xem role',
  apprentice_seer: 'Chọn người để soi phe',
  clairvoyant: 'Chọn 2 người để so sánh phe',
  detective: 'Chọn người để tra Sói',
  guard: 'Chọn người để bảo vệ',
  priest: 'Chọn người để miễn nhiễm',
  witch: 'Chọn hành động',
  hunter: 'Chọn người để đánh dấu',
  huntress: 'Chọn người để giết',
  cupid: 'Chọn 2 người để se duyên',
  clone: 'Chọn người để nhân bản',
  sorcerer: 'Chọn người để im lặng hóa',
  old_hag: 'Chọn người để bắt nghỉ',
  gambler: 'Chọn (ngẫu nhiên áp dụng)',
  werewolf: 'Chọn mục tiêu để cắn',
  lone_wolf: 'Chọn mục tiêu để cắn',
  alpha_wolf: 'Chọn người để biến thành Sói',
  wolf_seer: 'Chọn người để soi phe',
  medium: 'Chọn người để soi phe',
  solo_killer: 'Chọn người để giết',
  vampire: 'Chọn người để hút máu',
  cult_leader: 'Chọn người để chiêu mộ',
  saboteur: 'Chọn 1 người (người còn lại chọn ngẫu nhiên)',
}

export default function NightActionPanel({ request, selectedSeat, selectedSeat2, onSubmit }) {
  const [subtype, setSubtype] = useState(null)

  if (!request) return null
  const { action_type: actionType, needs_second_target: needsSecond } = request

  const canConfirm = actionType === 'witch' ? !!subtype && selectedSeat != null : selectedSeat != null || request.valid_targets.length === 0

  return (
    <div
      className="rounded-xl p-3.5 mb-3"
      style={{ background: 'rgba(255,123,0,0.08)', border: '1px solid rgba(255,123,0,0.3)' }}
    >
      <p className="font-bold mb-2" style={{ color: 'var(--text-strong)' }}>
        🌙 {ACTION_LABELS[actionType] || 'Hành động ban đêm'}
      </p>

      {actionType === 'witch' && (
        <div className="flex gap-2 mb-2">
          <button
            type="button"
            onClick={() => setSubtype('heal')}
            className="px-3 py-1 rounded-lg text-sm"
            style={{
              background: subtype === 'heal' ? 'var(--success)' : 'var(--input-bg)',
              color: subtype === 'heal' ? '#fff' : 'var(--text)',
              border: '1px solid ' + (subtype === 'heal' ? 'var(--success)' : 'var(--input-border)'),
            }}
          >
            Bình cứu
          </button>
          <button
            type="button"
            onClick={() => setSubtype('poison')}
            className="px-3 py-1 rounded-lg text-sm"
            style={{
              background: subtype === 'poison' ? 'var(--accent-red)' : 'var(--input-bg)',
              color: subtype === 'poison' ? '#fff' : 'var(--text)',
              border: '1px solid ' + (subtype === 'poison' ? 'var(--accent-red)' : 'var(--input-border)'),
            }}
          >
            Bình độc
          </button>
        </div>
      )}

      <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>
        {selectedSeat != null ? `Đã chọn ghế ${selectedSeat}` : 'Bấm vào một ghế trong vòng tròn để chọn'}
        {needsSecond && (selectedSeat2 != null ? `, ghế ${selectedSeat2}` : ' và một ghế nữa')}
      </p>

      <button type="button" disabled={!canConfirm} onClick={() => onSubmit(selectedSeat, subtype, selectedSeat2)} className="btn btn-primary">
        Xác nhận
      </button>
    </div>
  )
}
