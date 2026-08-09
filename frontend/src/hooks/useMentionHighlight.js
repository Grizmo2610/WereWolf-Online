export function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

export function useMentionHighlight(message, mySeatNumber, myDisplayName) {
  if (!message || mySeatNumber == null) return false
  const patterns = [
    new RegExp(`(?<!\\d)${mySeatNumber}(?!\\d)`, 'g'),
    new RegExp(`#${mySeatNumber}(?!\\d)`, 'g'),
  ]
  if (myDisplayName) {
    patterns.push(new RegExp(`\\b${escapeRegex(myDisplayName)}\\b`, 'gi'))
  }
  return patterns.some((p) => p.test(message))
}
