import { FlaskConical, Loader2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import SimulationResult from '../components/Simulation/SimulationResult'
import { getRecentPatients, simulateTreatment } from '../services/api'
import { type Patient, type SimulationResponse } from '../types'

const Simulation = (): JSX.Element => {
  const [patients, setPatients] = useState<Patient[]>([])
  const [patientId, setPatientId] = useState<string>('')
  const [hypothesis, setHypothesis] = useState<string>('')
  const [result, setResult] = useState<SimulationResponse | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)

  useEffect(() => {
    const loadPatients = async (): Promise<void> => {
      const response = await getRecentPatients()
      setPatients(response)
      setPatientId(response[0]?.id ?? '')
    }

    void loadPatients()
  }, [])

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault()
    if (!patientId || !hypothesis.trim()) {
      return
    }

    setIsLoading(true)
    try {
      const response = await simulateTreatment({
        patient_id: patientId,
        treatment_hypothesis: hypothesis,
      })
      setResult(response)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6">
        <h2 className="mb-4 text-xl font-semibold text-[color:#1e3a5f]">Simulation therapeutique</h2>

        <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-[220px_1fr_auto] md:items-end">
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Patient</label>
            <select
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
              required
            >
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.id} - {patient.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Hypothese de traitement</label>
            <textarea
              value={hypothesis}
              onChange={(event) => setHypothesis(event.target.value)}
              className="h-24 w-full resize-y rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder="Ex: Intensifier la prise en charge antihypertensive et augmenter l activite physique quotidienne"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-[color:#1e3a5f] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[color:#16304d] disabled:opacity-70"
          >
            {isLoading ? <Loader2 className="animate-spin" size={16} /> : <FlaskConical size={16} />}
            Lancer la simulation
          </button>
        </form>
      </section>

      {result ? <SimulationResult result={result} /> : null}
    </div>
  )
}

export default Simulation
