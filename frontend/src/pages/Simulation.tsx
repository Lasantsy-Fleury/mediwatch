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
        <h2 className="mb-2 text-xl font-semibold text-[color:#1e3a5f]">Simulation Thérapeutique</h2>
        <p className="mb-6 text-sm text-slate-600">
          Utilisez notre moteur d'IA pour projeter l'impact potentiel d'une modification de traitement ou d'hygiène de vie sur les indicateurs de santé du patient.
        </p>

        <form onSubmit={handleSubmit} className="grid gap-6 md:grid-cols-[250px_1fr_auto] md:items-end">
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Sélection du Patient</label>
            <select
              value={patientId}
              onChange={(event) => setPatientId(event.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              required
            >
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.name} (ID: {patient.id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">Hypothèse Thérapeutique</label>
            <textarea
              value={hypothesis}
              onChange={(event) => setHypothesis(event.target.value)}
              className="h-24 w-full resize-none rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              placeholder="Exemple : Introduction d'un inhibiteur de l'ECA et recommandation de 30 min de marche quotidienne..."
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-[color:#1e3a5f] px-6 py-3 text-sm font-semibold text-white transition hover:bg-[color:#16304d] disabled:opacity-70"
          >
            {isLoading ? <Loader2 className="animate-spin" size={16} /> : <FlaskConical size={16} />}
            Lancer l'analyse
          </button>
        </form>
      </section>

      {result ? <SimulationResult result={result} /> : null}
    </div>
  )
}

export default Simulation
