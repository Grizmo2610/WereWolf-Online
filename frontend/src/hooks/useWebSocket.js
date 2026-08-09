import { useEffect, useRef } from 'react'
import { WS_BASE } from '../api/client'
import { useGameStore } from '../store/gameStore'

const RECONNECT_DELAY_MS = 2000

export function useWebSocket(roomCode) {
  const socketRef = useRef(null)

  useEffect(() => {
    if (!roomCode) return
    let cancelled = false
    let reconnectTimer = null

    function connect() {
      if (cancelled) return
      const ws = new WebSocket(`${WS_BASE}/ws/${roomCode}`)
      socketRef.current = ws

      ws.onopen = () => useGameStore.getState().setConnected(true)

      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        dispatch(message.type, message.payload)
      }

      ws.onclose = () => {
        useGameStore.getState().setConnected(false)
        if (!cancelled) {
          reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS)
        }
      }

      ws.onerror = () => ws.close()
    }

    connect()

    return () => {
      cancelled = true
      clearTimeout(reconnectTimer)
      socketRef.current?.close()
    }
  }, [roomCode])

  const send = (type, payload = {}) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ type, payload }))
    }
  }

  return { send }
}

function dispatch(type, payload) {
  const store = useGameStore.getState()
  const handlers = {
    ROOM_UPDATE: store.handleRoomUpdate,
    ROOM_SETTINGS_UPDATE: store.handleRoomSettingsUpdate,
    GAME_START: store.handleGameStart,
    ROLE_ASSIGNED: store.handleRoleAssigned,
    WOLF_SEATS: store.handleWolfSeats,
    PHASE_CHANGE: store.handlePhaseChange,
    NIGHT_ACTION_REQUEST: store.handleNightActionRequest,
    NIGHT_INFO_RESULT: store.handleNightInfoResult,
    PLAYER_SPEAK: store.handlePlayerSpeak,
    DEAD_CHAT: store.handleDeadChat,
    VOTE_UPDATE: store.handleVoteUpdate,
    SKIP_VOTE_UPDATE: store.handleSkipVoteUpdate,
    PHASE_RESULT: store.handlePhaseResult,
    PLAYER_DISCONNECTED: store.handlePlayerDisconnected,
    PLAYER_RECONNECTED: store.handlePlayerReconnected,
    HOST_TRANSFERRED: store.handleHostTransferred,
    GAME_END: store.handleGameEnd,
  }
  const handler = handlers[type]
  if (handler) handler(payload)

  if (type === 'GAME_START') {
    store.initPlayersFromSeats()
  }
}
