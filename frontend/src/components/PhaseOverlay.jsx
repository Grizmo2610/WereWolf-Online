import { AnimatePresence, motion } from 'framer-motion'

export default function PhaseOverlay({ phase }) {
  return (
    <AnimatePresence>
      {phase === 'night' && (
        <motion.div
          className="fixed inset-0 pointer-events-none z-10"
          style={{ background: 'radial-gradient(ellipse at bottom, #0d1420 0%, #030407 100%)' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.7 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.2 }}
        />
      )}
    </AnimatePresence>
  )
}
