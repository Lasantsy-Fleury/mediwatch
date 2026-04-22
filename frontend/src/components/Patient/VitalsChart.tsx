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
import { type VitalsPoint } from '../../types'

interface LineConfig {
  dataKey: keyof VitalsPoint
  name: string
  color: string
}

interface VitalsChartProps {
  title: string
  data: VitalsPoint[]
  lines: LineConfig[]
  yUnit?: string
}

const VitalsChart = ({ title, data, lines, yUnit }: VitalsChartProps): JSX.Element => {
  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 md:p-5">
      <h3 className="mb-4 text-base font-semibold text-[color:#1e3a5f]">{title}</h3>
      <div className="h-72 w-full">
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 8, right: 16, left: 4, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="date" tick={{ fill: '#475569', fontSize: 12 }} />
            <YAxis tick={{ fill: '#475569', fontSize: 12 }} unit={yUnit} />
            <Tooltip />
            <Legend />
            {lines.map((line) => (
              <Line
                key={line.name}
                type="monotone"
                dataKey={line.dataKey}
                name={line.name}
                stroke={line.color}
                strokeWidth={2.4}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  )
}

export default VitalsChart
