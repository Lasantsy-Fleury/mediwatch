import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { type SimulationResponse } from '../../types'

interface SimulationResultProps {
  result: SimulationResponse
}

const SimulationResult = ({ result }: SimulationResultProps): JSX.Element => {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-[color:#1e3a5f]">Trajectoire simulee</h3>
        <p className="text-sm text-slate-600">Hypothese: {result.treatment_hypothesis}</p>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer>
          <LineChart data={result.trajectory} margin={{ top: 8, right: 16, left: 4, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="day" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="risk_index" name="Indice de risque" stroke="#ef4444" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="systolic" name="TA systolique" stroke="#3b82f6" strokeWidth={2.2} dot={false} />
            <Line type="monotone" dataKey="glucose" name="Glycemie" stroke="#10b981" strokeWidth={2.2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}

export default SimulationResult
