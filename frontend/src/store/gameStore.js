import { create } from 'zustand'

let feedIdCounter = 0
const nextFeedId = () => `feed-${++feedIdCounter}-${Date.now()}`

const initialState = {
  roomCode: null,
  mySeatId: null,
  hostSeatId: null,
  seats: [], // [{seat_id, display_name, is_ready}]
  status: 'waiting', // waiting | in_progress | finished
  roomSettings: null, // {reveal_on_death, discussion_seconds, early_vote_after_seconds, vote_seconds, night_seconds}

  phase: 'lobby', // lobby | night | discussion | vote | ended
  round: 0,
  phaseDurationSeconds: 0,
  phaseStartedAt: null,

  players: {}, // seat_id -> {display_name, is_alive}
  totalPlayers: 0,
  roleCounts: {},

  myRole: null, // {role_id, role_meta}
  wolfSeatIds: null,
  nightActionRequest: null, // {action_type, valid_targets, needs_second_target}
  nightInfoResults: [], // history of private info received

  voteCounts: {}, // seat_id -> count, live during VOTE phase
  totalVoted: 0,
  totalEligible: 0,
  skipCount: 0,
  skipRequired: 0,

  feed: [], // unified chat/banner/dead-chat/vote-counter feed

  winnerFaction: null,
  allRolesReveal: null,

  isConnected: false,
}

export const useGameStore = create((set) => ({
  ...initialState,

  reset: () => set(initialState),

  setMySeatId: (seatId) => set({ mySeatId: seatId }),
  setConnected: (isConnected) => set({ isConnected }),

  handleRoomUpdate: (payload) =>
    set({ seats: payload.players, hostSeatId: payload.host_seat_id }),

  handleRoomSettingsUpdate: (payload) => set({ roomSettings: payload }),

  handleGameStart: (payload) =>
    set((state) => ({
      status: 'in_progress',
      totalPlayers: payload.total_players,
      roleCounts: payload.role_counts,
      feed: [
        ...state.feed,
        banner(`Ván đấu bắt đầu — ${payload.total_players} người chơi`, 'info'),
      ],
    })),

  handleRoleAssigned: (payload) =>
    set({ myRole: { roleId: payload.role_id, meta: payload.role_meta } }),

  handleWolfSeats: (payload) => set({ wolfSeatIds: payload.wolf_seat_ids }),

  handlePhaseChange: (payload) =>
    set((state) => ({
      phase: payload.phase,
      round: payload.round,
      phaseDurationSeconds: payload.duration_seconds,
      phaseStartedAt: payload.started_at,
      nightActionRequest: payload.phase === 'night' ? state.nightActionRequest : null,
      voteCounts: payload.phase === 'vote' ? {} : state.voteCounts,
      totalVoted: 0,
      skipCount: 0,
      feed: [...state.feed, banner(phaseLabel(payload.phase, payload.round), 'phase')],
    })),

  handleNightActionRequest: (payload) => set({ nightActionRequest: payload }),

  handleNightInfoResult: (payload) =>
    set((state) => ({ nightInfoResults: [...state.nightInfoResults, payload] })),

  handlePlayerSpeak: (payload) =>
    set((state) => ({ feed: [...state.feed, chatBubble(payload, 'public')] })),

  handleDeadChat: (payload) =>
    set((state) => ({ feed: [...state.feed, chatBubble(payload, 'dead')] })),

  handleVoteUpdate: (payload) =>
    set({ voteCounts: payload.counts, totalVoted: payload.total_voted, totalEligible: payload.total_eligible }),

  handleSkipVoteUpdate: (payload) =>
    set({ skipCount: payload.skip_count, skipRequired: payload.required }),

  handlePhaseResult: (payload) =>
    set((state) => {
      const players = { ...state.players }
      const banners = []
      if (payload.no_kill) {
        banners.push(banner('Đêm qua không có ai chết.', 'safe'))
      }
      for (const death of payload.deaths || []) {
        if (players[death.seat_id]) {
          players[death.seat_id] = { ...players[death.seat_id], is_alive: !death.revealed_only }
        }
        banners.push(
          death.revealed_only
            ? banner(`Ghế ${death.seat_id} (${death.display_name}) được miễn nhiễm — lộ bài công khai.`, 'reveal')
            : banner(deathLabel(death), 'death')
        )
      }
      return { players, feed: [...state.feed, ...banners] }
    }),

  handlePlayerDisconnected: (payload) =>
    set((state) => ({ feed: [...state.feed, banner(`Ghế ${payload.seat_id} mất kết nối.`, 'warn')] })),

  handlePlayerReconnected: (payload) =>
    set((state) => ({ feed: [...state.feed, banner(`Ghế ${payload.seat_id} đã kết nối lại.`, 'info')] })),

  handleHostTransferred: (payload) =>
    set((state) => ({ hostSeatId: payload.new_host_seat_id, feed: [...state.feed, banner(`Ghế ${payload.new_host_seat_id} trở thành chủ phòng mới.`, 'info')] })),

  handleGameEnd: (payload) =>
    set((state) => ({
      status: 'finished',
      phase: 'ended',
      winnerFaction: payload.winner_faction,
      allRolesReveal: payload.all_roles,
      feed: [...state.feed, banner(winnerLabel(payload.winner_faction), 'end')],
    })),

  initPlayersFromSeats: () =>
    set((state) => {
      const players = {}
      for (const seat of state.seats) {
        players[seat.seat_id] = { display_name: seat.display_name, is_alive: true }
      }
      return { players }
    }),
}))

function banner(text, kind) {
  return { id: nextFeedId(), type: 'banner', kind, text, ts: Date.now() }
}

function chatBubble(payload, channel) {
  return {
    id: nextFeedId(),
    type: 'chat',
    channel,
    seatId: payload.seat_id,
    displayName: payload.display_name,
    text: payload.text,
    ts: Date.now(),
  }
}

function phaseLabel(phase, round) {
  const names = { night: 'Đêm', discussion: 'Thảo luận', vote: 'Bỏ phiếu', morning: 'Buổi sáng' }
  return `— ${names[phase] || phase} (Ngày/Đêm ${round}) —`
}

function deathLabel(death) {
  const causes = {
    wolf_bite: 'bị Sói cắn chết',
    lynch: 'bị trục xuất',
    witch_poison: 'bị đầu độc',
    hunter_mark: 'bị Thợ Săn kéo theo',
    terrorist: 'bị Khủng Bố kéo theo',
    cupid_link: 'chết theo bạn tình',
    solo_killer: 'bị Sát Nhân Đơn Độc giết',
    vampire: 'bị Ma Cà Rồng hút máu',
    huntress: 'bị Nữ Thợ Săn giết',
    gambler_miss: 'thua canh bạc và tự thiệt mạng',
  }
  return `💀 Ghế ${death.seat_id} (${death.display_name}) — ${causes[death.cause] || death.cause}${death.role ? ` [${death.role}]` : ''}`
}

function winnerLabel(faction) {
  const names = {
    villagers: 'Phe Dân Làng',
    wolves: 'Phe Sói',
    fool: 'Kẻ Chán Đời',
    twins: 'Cặp Song Sinh',
    lone_wolf: 'Sói Cô Độc',
    solo_killer: 'Sát Nhân Đơn Độc',
    vampire: 'Ma Cà Rồng',
    cult: 'Giáo Phái',
  }
  return `🏆 ${names[faction] || faction} chiến thắng!`
}
