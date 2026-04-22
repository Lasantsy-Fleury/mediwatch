import { ClipboardList } from 'lucide-react'
import { useEffect, useState } from 'react'
import ConsultationForm from '../components/Consultation/ConsultationForm'
import RiskBadge from '../components/Consultation/RiskBadge'
import { getRecentPatients, submitConsultation } from '../services/api'
import { type ConsultationPayload, type ConsultationResult, type Patient } from '../types'

const Consultation = (): JSX.Element => {
  const [patients, setPatients] = useState<Patient[]>([])
  const [result, setResult] = useState<ConsultationResult | null>(null)
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)

  useEffect(() => {
    const loadPatients = async (): Promise<void> => {
      const response = await getRecentPatients()
      setPatients(response)
    }

    void loadPatients()
  }, [])

  const handleSubmit = async (payload: ConsultationPayload): Promise<void> => {
    setIsSubmitting(true)
    try {
      const response = await submitConsultation(payload)
      setResult(response)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1.25fr_1fr]">
      <ConsultationForm patients={patients} onSubmit={handleSubmit} isSubmitting={isSubmitting} />

      <section className="rounded-lg border border-slate-200 bg-white p-5 md:p-6">
        <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-[color:#1e3a5f]">
          <ClipboardList size={18} /> Resultat clinique
        </h3>

        {!result ? (
          <p className="rounded-lg bg-slate-50 p-4 text-sm text-slate-600">
            Soumettez une consultation pour afficher le resume structure, les risques prioritaires et les suggestions de questions.
          </p>
        ) : (
          <div className="space-y-6">
            <article>
              <h4 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Resume structure</h4>
              <p className="rounded-lg bg-slate-50 p-4 text-sm leading-relaxed text-slate-700">{result.structured_summary}</p>
            </article>

            <article>
              <h4 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Risques prioritaires</h4>
              <div className="space-y-3">
                {result.prioritized_risks.map((risk) => (
                  <div key={risk.label} className="rounded-lg border border-slate-200 p-3">
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <p className="font-semibold text-slate-700">{risk.label}</p>
                      <RiskBadge level={risk.level} />
                    </div>
                    <p className="text-sm text-slate-600">{risk.reason}</p>
                  </div>
                ))}
              </div>
            </article>

            <article>
              <h4 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">Questions a poser</h4>
              <ul className="space-y-2 text-sm text-slate-700">
                {result.suggested_questions.map((question) => (
                  <li key={question} className="rounded-lg bg-slate-50 p-3">
                    {question}
                  </li>
                ))}
              </ul>
            </article>
          </div>
        )}
      </section>
    </div>
  )
}

export default Consultation
