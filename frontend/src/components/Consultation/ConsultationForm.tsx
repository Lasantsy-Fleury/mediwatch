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
      image: imageBase64,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-slate-200 bg-white p-5 md:p-6">
      <div>
        <label htmlFor="patientId" className="mb-2 block text-sm font-semibold text-slate-700">
          Patient (ID)
        </label>
        <input
          id="patientId"
          list="patients-list"
          value={patientId}
          onChange={(event) => setPatientId(event.target.value)}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-blue-100 transition focus:border-blue-400 focus:ring"
          placeholder="Ex: PT-1001"
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
          Note clinique
        </label>
        <textarea
          id="noteText"
          value={noteText}
          onChange={(event) => setNoteText(event.target.value)}
          className="h-44 w-full resize-y rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none ring-blue-100 transition focus:border-blue-400 focus:ring"
          placeholder="Saisissez l observation clinique, les symptomes, le contexte et les hypotheses..."
          required
        />
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-slate-700">Parametres vitaux</h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <label className="text-sm text-slate-600">
            Systolique
            <input
              type="number"
              value={vitals.systolic}
              onChange={(event) => updateVital('systolic', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Diastolique
            <input
              type="number"
              value={vitals.diastolic}
              onChange={(event) => updateVital('diastolic', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Frequence cardiaque
            <input
              type="number"
              value={vitals.heart_rate}
              onChange={(event) => updateVital('heart_rate', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
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
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Glycemie (mg/dL)
            <input
              type="number"
              value={vitals.glucose}
              onChange={(event) => updateVital('glucose', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            Temperature (deg C)
            <input
              type="number"
              step="0.1"
              value={vitals.temperature}
              onChange={(event) => updateVital('temperature', event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              required
            />
          </label>
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-semibold text-slate-700">Image clinique (optionnelle)</label>
        <label className="flex cursor-pointer items-center gap-3 rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-600">
          <ImagePlus size={16} />
          Importer une image
          <input type="file" accept="image/*" className="hidden" onChange={onImageChange} />
        </label>
        {previewSrc ? (
          <img src={previewSrc} alt="Apercu" className="mt-3 h-40 w-full rounded-lg object-cover" />
        ) : null}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="inline-flex items-center gap-2 rounded-lg bg-[color:#1e3a5f] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[color:#16304d] disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isSubmitting ? <Loader2 className="animate-spin" size={16} /> : <Send size={16} />}
        Analyser cette consultation
      </button>
    </form>
  )
}

export default ConsultationForm
