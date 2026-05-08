import { AlertTriangle, ArrowRight, Clock3 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { type Patient } from '../../types'

interface PatientCardProps {
  patient: Patient
}

const PatientCard = ({ patient }: PatientCardProps): JSX.Element => {
  return (
    <Link
      to={`/patient/${patient.id}`}
      className="group block rounded-lg border border-slate-200 bg-white p-5 transition hover:shadow-md hover:border-blue-200"
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold text-[color:#1e3a5f] group-hover:text-blue-700 transition-colors">{patient.name}</h3>
          <p className="text-sm text-slate-500 font-mono">ID: {patient.id}</p>
        </div>
        <ArrowRight className="text-slate-400 transition group-hover:translate-x-1 group-hover:text-blue-500" size={18} />
      </div>

      <div className="mt-4 space-y-2 text-sm text-slate-600">
        <p className="flex items-center gap-2">
          <Clock3 size={14} className="text-slate-400" />
          Dernière consultation : {patient.last_consultation}
        </p>
        <p className="flex items-center gap-2">
          <AlertTriangle size={14} className={`${patient.active_alerts > 0 ? 'text-amber-500' : 'text-slate-300'}`} />
          {patient.active_alerts} alerte{patient.active_alerts > 1 ? 's' : ''} active{patient.active_alerts > 1 ? 's' : ''}
        </p>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {patient.comorbidities.map((item) => (
          <span key={item} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 border border-slate-200">
            {item}
          </span>
        ))}
      </div>
    </Link>
  )
}

export default PatientCard
