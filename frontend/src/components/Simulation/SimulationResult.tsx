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
  const chartData = result.trajectory.map((point) => ({
    day: `J+${point.day}`,
    predicted: point.predicted_value,
    lower: point.confidence_lower,
    upper: point.confidence_upper,
  }))

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-[color:#1e3a5f]">Projection de l'Évolution Clinique</h3>
        <div className="mt-2 space-y-1">
          <p className="text-sm text-slate-600">
            <span className="font-medium">Hypothèse :</span> {result.treatment_description}
          </p>
          <div className="flex items-center gap-2">
            <p className="text-sm text-slate-600">Risque de décompensation estimé :</p>
            <span className={`text-sm font-bold ${result.decompensation_risk > 0.5 ? 'text-red-600' : 'text-emerald-600'}`}>
              {Math.round(result.decompensation_risk * 100)}%
            </span>
          </div>
        </div>
      </div>

      <div className="h-80 w-full">
        <ResponsiveContainer>
          <LineChart data={chartData} margin={{ top: 8, right: 16, left: 4, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
            <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
            <Tooltip
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Legend verticalAlign="top" align="right" height={36} iconType="circle" />
            <Line
              type="monotone"
              dataKey="predicted"
              name="Valeur projetée"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={{ r: 4, fill: '#3b82f6' }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="lower"
              name="Intervalle inférieur"
              stroke="#94a3b8"
              strokeDasharray="5 5"
              strokeWidth={1.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="upper"
              name="Intervalle supérieur"
              stroke="#94a3b8"
              strokeDasharray="5 5"
              strokeWidth={1.5}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 rounded-lg bg-slate-50 p-4 border border-slate-100">
        <h4 className="mb-2 text-sm font-semibold text-slate-700">Analyse Narrative</h4>
        <p className="text-sm leading-relaxed text-slate-600 italic">"{result.narrative}"</p>
      </div>

      {result.warnings.length > 0 ? (
        <div className="mt-4">
          <h4 className="mb-2 text-sm font-semibold text-amber-800">Points de Vigilance</h4>
          <ul className="space-y-2 text-sm">
            {result.warnings.map((warning, index) => (
              <li key={index} className="flex items-start gap-2 rounded-md bg-amber-50 px-3 py-2 text-amber-700 border border-amber-100">
                <span className="mt-1 flex h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                {warning}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  )
}

export default SimulationResult
