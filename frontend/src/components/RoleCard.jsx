import { motion } from 'framer-motion'

const FACTION_LABELS = { villager: 'Dân Làng', wolf: 'Sói', neutral: 'Trung Lập' }

export default function RoleCard({ role }) {
  if (!role) return null
  const { meta } = role

  return (
    <motion.div
      initial={{ rotateY: 180, opacity: 0 }}
      animate={{ rotateY: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="glass-card p-5 max-w-sm"
    >
      <div className="text-xs uppercase tracking-wide mb-1 font-bold" style={{ color: 'var(--accent-orange)' }}>
        {FACTION_LABELS[meta.faction] || meta.faction}
      </div>
      <div className="text-2xl font-extrabold mb-2" style={{ color: 'var(--text-strong)' }}>
        {meta.display_name_vi}
      </div>
      <p className="text-sm leading-relaxed" style={{ color: 'var(--text)' }}>
        {meta.description_vi}
      </p>
    </motion.div>
  )
}
