import { type RiskLevel } from '../../types'

interface RiskBadgeProps {
  level: RiskLevel
}

const styles: Record<RiskLevel, string> = {
  low: 'bg-emerald-100 text-emerald-700 ring-emerald-200',
  medium: 'bg-amber-100 text-amber-700 ring-amber-200',
  high: 'bg-red-100 text-red-700 ring-red-200',
}

const labels: Record<RiskLevel, string> = {
  low: 'Faible',
  medium: 'Modere',
  high: 'Eleve',
}

const RiskBadge = ({ level }: RiskBadgeProps): JSX.Element => {
  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ring-1 ${styles[level]}`}>{labels[level]}</span>
}

export default RiskBadge
