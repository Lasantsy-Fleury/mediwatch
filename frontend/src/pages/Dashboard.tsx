import { Activity, AlertTriangle, ShieldAlert } from 'lucide-react'
import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import PatientCard from '../components/Patient/PatientCard'
import { getDashboardStats, getRecentPatients, getWeeklyConsultations } from '../services/api'
import { type DashboardStats, type Patient, type WeeklyConsultationStat } from '../types'

const Dashboard = (): JSX.Element => {
  const [patients, setPatients] = useState<Patient[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [weeklyData, setWeeklyData] = useState<WeeklyConsultationStat[]>([])

  useEffect(() => {
    const loadData = async (): Promise<void> => {
      const [patientsResponse, statsResponse, weeklyResponse] = await Promise.all([
        getRecentPatients(),
        getDashboardStats(),
        getWeeklyConsultations(),
      ])
      setPatients(patientsResponse)
      setStats(statsResponse)
      setWeeklyData(weeklyResponse)
    }

    void loadData()
  }, [])

  return (
    <div className="space-y-7">
      <section className="grid gap-4 lg:grid-cols-3">
        <article className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="mb-2 flex items-center gap-2 text-sm text-slate-500">
            <Activity size={16} className="text-[color:#3b82f6]" /> Consultations du jour
          </p>
          <p className="text-3xl font-bold text-[color:#1e3a5f]">{stats?.consultations_today ?? '--'}</p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="mb-2 flex items-center gap-2 text-sm text-slate-500">
            <AlertTriangle size={16} className="text-[color:#f59e0b]" /> Alertes actives
          </p>
          <p className="text-3xl font-bold text-[color:#1e3a5f]">{stats?.active_alerts ?? '--'}</p>
        </article>
        <article className="rounded-lg border border-slate-200 bg-white p-5">
          <p className="mb-2 flex items-center gap-2 text-sm text-slate-500">
            <ShieldAlert size={16} className="text-[color:#ef4444]" /> Patients a risque
          </p>
          <p className="text-3xl font-bold text-[color:#1e3a5f]">{stats?.high_risk_patients ?? '--'}</p>
        </article>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6">
        <h3 className="mb-4 text-lg font-semibold text-[color:#1e3a5f]">Consultations par semaine</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer>
            <BarChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="consultations" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-[color:#1e3a5f]">Patients recents</h3>
          <p className="text-sm text-slate-500">Cliquez sur une carte pour ouvrir le dossier</p>
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          {patients.map((patient) => (
            <PatientCard key={patient.id} patient={patient} />
          ))}
        </div>
      </section>
    </div>
  )
}

export default Dashboard
