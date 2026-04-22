import { AlertCircle, FileText, Pill } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import VitalsChart from '../components/Patient/VitalsChart'
import { getPatientTimeline } from '../services/api'
import { type PatientTimelineResponse, type RiskLevel } from '../types'

const severityClass: Record<RiskLevel, string> = {
  low: 'bg-emerald-500',
  medium: 'bg-amber-500',
  high: 'bg-red-500',
}

const riskBarColor = (value: number): string => {
  if (value >= 70) {
    return 'bg-red-500'
  }
  if (value >= 40) {
    return 'bg-amber-500'
  }
  return 'bg-emerald-500'
}

const Patient = (): JSX.Element => {
  const { id = 'PT-1001' } = useParams()
  const [data, setData] = useState<PatientTimelineResponse | null>(null)

  useEffect(() => {
    const loadPatient = async (): Promise<void> => {
      const response = await getPatientTimeline(id)
      setData(response)
    }

    void loadPatient()
  }, [id])

  const patient = data?.patient
  const timeline = useMemo(() => data?.timeline ?? [], [data?.timeline])
  const series = useMemo(() => data?.vitals_series ?? [], [data?.vitals_series])

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6">
        {patient ? (
          <div className="grid gap-4 lg:grid-cols-[1.3fr_1fr]">
            <div>
              <p className="text-sm uppercase tracking-[0.16em] text-slate-500">Dossier patient</p>
              <h2 className="mt-1 text-2xl font-bold text-[color:#1e3a5f]">{patient.name}</h2>
              <p className="mt-2 text-sm text-slate-600">{patient.age} ans</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {patient.comorbidities.map((item) => (
                  <span key={item} className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700">
                    {item}
                  </span>
                ))}
              </div>
            </div>
            <div className="rounded-lg bg-slate-50 p-4">
              <p className="mb-2 text-xs uppercase tracking-wide text-slate-500">Traitement actuel</p>
              <p className="text-sm font-medium text-slate-700">{patient.current_treatment}</p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-600">Chargement du dossier...</p>
        )}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6">
        <h3 className="mb-4 text-lg font-semibold text-[color:#1e3a5f]">Timeline clinique</h3>
        <div className="space-y-3">
          {timeline.map((event) => (
            <article key={event.id} className="rounded-lg border border-slate-200 p-4">
              <div className="mb-2 flex items-center justify-between gap-3">
                <p className="font-semibold text-slate-700">{event.title}</p>
                <span className="text-xs text-slate-500">{event.date}</span>
              </div>
              <p className="text-sm text-slate-600">{event.details}</p>
              <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
                {event.type === 'note' ? <FileText size={14} /> : null}
                {event.type === 'alert' ? <AlertCircle size={14} /> : null}
                {event.type === 'prescription' ? <Pill size={14} /> : null}
                <span className="capitalize">{event.type}</span>
                {event.severity ? <span className={`h-2.5 w-2.5 rounded-full ${severityClass[event.severity]}`} /> : null}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-5">
        <VitalsChart
          title="Tension arterielle"
          data={series}
          yUnit=" mmHg"
          lines={[
            { dataKey: 'systolic', name: 'Systolique', color: '#3b82f6' },
            { dataKey: 'diastolic', name: 'Diastolique', color: '#1e3a5f' },
          ]}
        />
        <VitalsChart
          title="Frequence cardiaque"
          data={series}
          yUnit=" bpm"
          lines={[{ dataKey: 'heart_rate', name: 'FC', color: '#10b981' }]}
        />
        <VitalsChart
          title="Poids et glycemie"
          data={series}
          lines={[
            { dataKey: 'weight', name: 'Poids', color: '#f59e0b' },
            { dataKey: 'glucose', name: 'Glycemie', color: '#ef4444' },
          ]}
        />
      </section>

      {data ? (
        <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6">
          <h3 className="mb-4 text-lg font-semibold text-[color:#1e3a5f]">Score de surveillance</h3>
          <div className="grid gap-4 md:grid-cols-3">
            {Object.entries(data.risk_scores).map(([key, value]) => (
              <article key={key} className="rounded-lg border border-slate-200 p-4">
                <p className="mb-2 text-sm font-semibold capitalize text-slate-700">{key}</p>
                <div className="h-3 rounded-full bg-slate-100">
                  <div className={`h-3 rounded-full ${riskBarColor(value)}`} style={{ width: `${value}%` }} />
                </div>
                <p className="mt-2 text-sm text-slate-600">{value}/100</p>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}

export default Patient
