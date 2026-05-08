import { ImagePlus, Loader2, Send } from 'lucide-react'
import { useMemo, useState } from 'react'
import { type ConsultationPayload, type Patient, type Vitals } from '../../types'

interface ConsultationFormProps {
  patients: Patient[]
  onSubmit: (payload: ConsultationPayload) => Promise<void>
  isSubmitting: boolean
}

const initialVitals: Vitals = {
  systolic: 120,
  diastolic: 80,
  heart_rate: 72,
  weight: 70,
  glucose: 95,
  temperature: 36.8,
}

const ConsultationForm = ({ patients, onSubmit, isSubmitting }: ConsultationFormProps): JSX.Element => {
  const [patientId, setPatientId] = useState<string>(patients[0]?.id ?? '')
  const [noteText, setNoteText] = useState<string>('')
  const [vitals, setVitals] = useState<Vitals>(initialVitals)
  const [imageBase64, setImageBase64] = useState<string | undefined>(undefined)

  const previewSrc = useMemo(() => {
    if (!imageBase64) {
      return ''
    }
    return `data:image/*;base64,${imageBase64}`
  }, [imageBase64])

  const updateVital = <K extends keyof Vitals>(key: K, rawValue: string): void => {
    const value = Number(rawValue)
    setVitals((prev) => ({ ...prev, [key]: Number.isFinite(value) ? value : prev[key] }))
  }

  const onImageChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0]
    if (!file) {
      setImageBase64(undefined)
      return
    }

    const reader = new FileReader()
    reader.onload = () => {
      const result = typeof reader.result === 'string' ? reader.result : ''
      const base64 = result.includes(',') ? result.split(',')[1] : ''
      setImageBase64(base64 || undefined)
    }
    reader.readAsDataURL(file)
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault()
    await onSubmit({
      patient_id: patientId,
      note_text: noteText,
      vitals,
      image_base64: imageBase64,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-slate-200 bg-white p-5 md:p-6">
      <div>
        <label htmlFor="patientId" className="mb-2 block text-sm font-semibold text-slate-700">
          Sélection du Patient
        </label>
        <input
          id="patientId"
          list="patients-list"
          value={patientId}
          onChange={(event) => setPatientId(event.target.value)}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-blue-100 transition focus:border-blue-400 focus:ring"
          placeholder="Saisissez l'identifiant ou le nom..."
          required
        />
        <datalist id="patients-list">
          {patients.map((patient) => (
            <option key={patient.id} value={patient.id}>
              {patient.name}
            </option>
          ))}
        </datalist>
      </div>

      <div>
        <label htmlFor="noteText" className="mb-2 block text-sm font-semibold text-slate-700">
          Observations Cliniques
        </label>
        <textarea
          id="noteText"
          value={noteText}
          onChange={(event) => setNoteText(event.target.value)}
          className="h-44 w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-blue-100 transition focus:border-blue-400 focus:ring"
          placeholder="Décrivez les symptômes, le contexte clinique et vos hypothèses diagnostiques..."
          required
        />
      </div>

      <div>
        <h3 className="mb-4 text-sm font-semibold text-slate-700">Paramètres Vitaux</h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <label className="text-sm text-slate-600">
            Tension Systolique (mmHg)
            <input
              type="number"
              value={vitals.systolic}
              onChange={(event) => updateVital('systolic', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Tension Diastolique (mmHg)
            <input
              type="number"
              value={vitals.diastolic}
              onChange={(event) => updateVital('diastolic', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Fréquence Cardiaque (bpm)
            <input
              type="number"
              value={vitals.heart_rate}
              onChange={(event) => updateVital('heart_rate', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Poids (kg)
            <input
              type="number"
              step="0.1"
              value={vitals.weight}
              onChange={(event) => updateVital('weight', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Glycémie (mg/dL)
            <input
              type="number"
              value={vitals.glucose}
              onChange={(event) => updateVital('glucose', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Température (°C)
            <input
              type="number"
              step="0.1"
              value={vitals.temperature}
              onChange={(event) => updateVital('temperature', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-blue-500"
              required
            />
          </label>
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-semibold text-slate-700">Documents ou Clichés Cliniques (optionnel)</label>
        <label className="flex cursor-pointer items-center justify-center gap-3 rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-6 text-sm text-slate-600 transition hover:bg-slate-100">
          <ImagePlus size={20} className="text-slate-400" />
          <span>Glisser-déposer ou parcourir les fichiers</span>
          <input type="file" accept="image/*" className="hidden" onChange={onImageChange} />
        </label>
        {previewSrc ? (
          <div className="mt-3 relative inline-block">
             <img src={previewSrc} alt="Aperçu" className="h-40 w-full rounded-lg object-cover border border-slate-200" />
          </div>
        ) : null}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[color:#1e3a5f] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[color:#16304d] disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isSubmitting ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
        Soumettre pour Analyse Intelligente
      </button>
    </form>
  )
}

export default ConsultationForm
