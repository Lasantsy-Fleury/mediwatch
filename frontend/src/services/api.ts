import axios from 'axios'
import {
  type AuthUser,
  type ConsultationPayload,
  type ConsultationResult,
  type DashboardStats,
  type LoginPayload,
  type LoginResponse,
  type Patient,
  type PatientTimelineResponse,
  type RegisterPayload,
  type SocialLoginPayload,
  type SimulationPayload,
  type SimulationResponse,
  type WeeklyConsultationStat,
} from '../types'

interface ApiResponseEnvelope<T> {
  success: boolean
  data: T
  message?: string
  error?: string | null
}

interface BackendRiskScore {
  category?: string
  label?: string
  level?: string
  score?: number
  explanation?: string
}

interface BackendPatient {
  id: string
  first_name: string
  last_name: string
  age: number
  comorbidities?: Array<{ name?: string }>
  current_medications?: Array<{ name?: string; dosage?: string; frequency?: string }>
  created_at?: string
  risk_scores?: BackendRiskScore[]
}

interface BackendConsultation {
  consultation_id?: string
  timestamp?: string
  summary?: string
  alerts?: Array<{ message?: string; severity?: string; recommendation?: string }>
  raw_vitals_analysis?: {
    analyses?: Array<{ parameter?: string; value?: number }>
  }
}

interface BackendPatientTimeline {
  patient: BackendPatient
  consultations: BackendConsultation[]
  risk_scores: BackendRiskScore[]
}

interface BackendSimulationResponse {
  patient_id: string
  treatment_description: string
  duration_days: number
  trajectory: Array<{
    day: number
    parameter: string
    predicted_value: number
    confidence_lower: number
    confidence_upper: number
  }>
  decompensation_risk: number
  decompensation_day?: number | null
  narrative: string
  warnings: string[]
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
})

let bearerToken: string | null = null

api.interceptors.request.use((config) => {
  if (bearerToken) {
    config.headers.Authorization = `Bearer ${bearerToken}`
  }
  return config
})

export const setApiAccessToken = (token: string | null): void => {
  bearerToken = token
}

export const clearApiAccessToken = (): void => {
  bearerToken = null
}

const toRiskLevel = (value: string | undefined): 'low' | 'medium' | 'high' => {
  if (value === 'high' || value === 'critical') {
    return 'high'
  }
  if (value === 'medium' || value === 'warning') {
    return 'medium'
  }
  return 'low'
}

const mapRiskScores = (riskScores: BackendRiskScore[] | undefined): { cardio: number; metabolic: number; infectious: number } => {
  const mapped = {
    cardio: 0,
    metabolic: 0,
    infectious: 0,
  }

  for (const item of riskScores ?? []) {
    const category = (item.category ?? '').toLowerCase()
    const score = Math.round(Math.max(0, Math.min(1, item.score ?? 0)) * 100)
    if (category.includes('cardio')) {
      mapped.cardio = Math.max(mapped.cardio, score)
    } else if (category.includes('metab')) {
      mapped.metabolic = Math.max(mapped.metabolic, score)
    } else if (category.includes('infect')) {
      mapped.infectious = Math.max(mapped.infectious, score)
    }
  }

  return mapped
}

const mapPatient = (raw: BackendPatient): Patient => {
  const comorbidities = (raw.comorbidities ?? []).map((item) => item.name ?? '').filter(Boolean)
  const medicationLine = (raw.current_medications ?? [])
    .map((item) => [item.name, item.dosage, item.frequency].filter(Boolean).join(' '))
    .filter(Boolean)
    .join(', ')

  return {
    id: raw.id,
    name: `${raw.first_name} ${raw.last_name}`.trim(),
    age: raw.age,
    comorbidities,
    current_treatment: medicationLine,
    active_alerts: (raw.risk_scores ?? []).filter((item) => toRiskLevel(item.level) !== 'low').length,
    last_consultation: (raw.created_at ?? '').slice(0, 10),
    risk_scores: mapRiskScores(raw.risk_scores),
  }
}

const unwrapResponse = <T>(payload: ApiResponseEnvelope<T>): T => {
  if (!payload?.success) {
    throw new Error(payload?.error ?? payload?.message ?? 'Erreur API')
  }
  return payload.data
}

export const login = async (payload: LoginPayload): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/auth/login', payload)
  return response.data
}

export const register = async (payload: RegisterPayload): Promise<AuthUser> => {
  const response = await api.post<ApiResponseEnvelope<AuthUser>>('/auth/register', payload)
  return unwrapResponse(response.data)
}

export const socialLogin = async (payload: SocialLoginPayload): Promise<LoginResponse> => {
  const response = await api.post<LoginResponse>('/auth/social-login', payload)
  return response.data
}

export const getCurrentUser = async (): Promise<AuthUser> => {
  const response = await api.get<ApiResponseEnvelope<AuthUser>>('/auth/me')
  return unwrapResponse(response.data)
}

export const logout = async (): Promise<void> => {
  try {
    await api.post('/auth/logout')
  } catch {
    // Le backend est stateless : ignorer les erreurs logout réseau.
  }
}

const isConsultationResult = (value: unknown): value is ConsultationResult => {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const record = value as Record<string, unknown>
  return (
    typeof record.structured_summary === 'string' &&
    Array.isArray(record.prioritized_risks) &&
    Array.isArray(record.suggested_questions)
  )
}

const isPatientTimelineResponse = (value: unknown): value is PatientTimelineResponse => {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const record = value as Record<string, unknown>
  return (
    typeof record.patient === 'object' &&
    record.patient !== null &&
    Array.isArray(record.timeline) &&
    Array.isArray(record.vitals_series) &&
    typeof record.risk_scores === 'object' &&
    record.risk_scores !== null
  )
}

const isSimulationResponse = (value: unknown): value is SimulationResponse => {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const record = value as Record<string, unknown>
  return (
    typeof record.patient_id === 'string' &&
    typeof record.treatment_description === 'string' &&
    typeof record.duration_days === 'number' &&
    typeof record.decompensation_risk === 'number' &&
    Array.isArray(record.trajectory)
  )
}

export const submitConsultation = async (
  payload: ConsultationPayload,
): Promise<ConsultationResult> => {
  const requestPayload = {
    patient_id: payload.patient_id,
    note_text: payload.note_text,
    vitals: {
      systolic_bp: payload.vitals.systolic,
      diastolic_bp: payload.vitals.diastolic,
      heart_rate: payload.vitals.heart_rate,
      weight: payload.vitals.weight,
      glucose: Number((payload.vitals.glucose / 18).toFixed(2)),
      temperature: payload.vitals.temperature,
    },
    image_base64: payload.image_base64,
  }

  const response = await api.post<ApiResponseEnvelope<Record<string, unknown>>>('/consultation', requestPayload)

  const data = unwrapResponse(response.data)
  const riskScores = (data.risk_scores as BackendRiskScore[] | undefined) ?? []
  const result: ConsultationResult = {
    structured_summary: typeof data.summary === 'string' ? data.summary : '',
    prioritized_risks: riskScores.map((item) => ({
      label: item.label ?? item.category ?? 'Risque',
      level: toRiskLevel(item.level),
      score: Math.round(Math.max(0, Math.min(1, item.score ?? 0)) * 100),
      reason: item.explanation ?? 'Aucune explication fournie',
    })),
    suggested_questions: Array.isArray(data.suggested_questions)
      ? (data.suggested_questions as string[])
      : [],
  }

  if (isConsultationResult(result)) {
    return result
  }

  throw new Error('Format de reponse inattendu pour /consultation')
}

export const getPatientTimeline = async (
  patientId: string,
): Promise<PatientTimelineResponse> => {
  const response = await api.get<ApiResponseEnvelope<BackendPatientTimeline>>(`/patient/${patientId}/timeline`)
  const timeline = unwrapResponse(response.data)

  const patient = mapPatient(timeline.patient)
  const consultations = timeline.consultations ?? []

  const timelineEvents = consultations.flatMap((item, index) => {
    const date = (item.timestamp ?? '').slice(0, 10)
    const noteEvent = {
      id: `${item.consultation_id ?? `consult-${index}`}-note`,
      date,
      type: 'note' as const,
      title: 'Compte-rendu consultation',
      details: item.summary ?? 'Aucun resume',
      severity: 'low' as const,
    }

    const alertEvents = (item.alerts ?? []).map((alert, alertIndex) => ({
      id: `${item.consultation_id ?? `consult-${index}`}-alert-${alertIndex}`,
      date,
      type: 'alert' as const,
      title: alert.message ?? 'Alerte clinique',
      details: alert.recommendation ?? 'Aucune recommandation',
      severity: toRiskLevel(alert.severity),
    }))

    return [noteEvent, ...alertEvents]
  })

  const vitalsSeries = consultations.map((item) => {
    const analyses = item.raw_vitals_analysis?.analyses ?? []
    const getValue = (parameter: string): number => {
      const found = analyses.find((entry) => entry.parameter === parameter)
      return Number(found?.value ?? 0)
    }

    return {
      date: (item.timestamp ?? '').slice(0, 10),
      systolic: getValue('systolic_bp'),
      diastolic: getValue('diastolic_bp'),
      heart_rate: getValue('heart_rate'),
      weight: getValue('weight'),
      glucose: Math.round(getValue('glucose') * 18),
      temperature: getValue('temperature'),
    }
  })

  const result: PatientTimelineResponse = {
    patient,
    timeline: timelineEvents,
    vitals_series: vitalsSeries,
    risk_scores: mapRiskScores(timeline.risk_scores),
  }

  if (isPatientTimelineResponse(result)) {
    return result
  }

  throw new Error('Format de reponse inattendu pour /patient/{id}/timeline')
}

export const simulateTreatment = async (
  payload: SimulationPayload,
): Promise<SimulationResponse> => {
  const response = await api.post<ApiResponseEnvelope<BackendSimulationResponse>>('/simulate-treatment', {
    patient_id: payload.patient_id,
    treatment_hypothesis: payload.treatment_hypothesis,
    duration_days: 21,
    target_parameter: 'systolic_bp',
  })
  const data = unwrapResponse(response.data)

  const result: SimulationResponse = {
    patient_id: data.patient_id,
    treatment_description: data.treatment_description,
    duration_days: data.duration_days,
    trajectory: data.trajectory,
    decompensation_risk: data.decompensation_risk,
    decompensation_day: data.decompensation_day ?? null,
    narrative: data.narrative,
    warnings: data.warnings,
  }

  if (isSimulationResponse(result)) {
    return result
  }

  throw new Error('Format de reponse inattendu pour /simulate-treatment')
}

export const getRecentPatients = async (): Promise<Patient[]> => {
  const response = await api.get<ApiResponseEnvelope<BackendPatient[]>>('/patients')
  const data = unwrapResponse(response.data)
  return data.map(mapPatient)
}

export const getWeeklyConsultations = async (): Promise<WeeklyConsultationStat[]> => {
  const patients = await getRecentPatients()
  const timelines = await Promise.all(
    patients.map(async (patient) => {
      try {
        const response = await api.get<ApiResponseEnvelope<BackendPatientTimeline>>(`/patient/${patient.id}/timeline`)
        return unwrapResponse(response.data)
      } catch {
        return null
      }
    }),
  )

  const allTimestamps = timelines
    .filter((item): item is BackendPatientTimeline => item !== null)
    .flatMap((item) => item.consultations.map((consultation) => consultation.timestamp ?? ''))
    .filter(Boolean)

  const today = new Date()
  const buckets: WeeklyConsultationStat[] = []

  for (let i = 5; i >= 0; i -= 1) {
    const end = new Date(today)
    end.setDate(today.getDate() - i * 7)
    const start = new Date(end)
    start.setDate(end.getDate() - 6)

    const consultations = allTimestamps.filter((value) => {
      const date = new Date(value)
      return date >= start && date <= end
    }).length

    buckets.push({
      week: i === 0 ? 'Cette semaine' : `S-${i}`,
      consultations,
    })
  }

  return buckets
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
  const [patients, weekly] = await Promise.all([getRecentPatients(), getWeeklyConsultations()])
  return {
    consultations_today: weekly[weekly.length - 1]?.consultations ?? 0,
    active_alerts: patients.reduce((sum, patient) => sum + patient.active_alerts, 0),
    high_risk_patients: patients.filter(
      (patient) =>
        patient.risk_scores.cardio >= 70 ||
        patient.risk_scores.metabolic >= 70 ||
        patient.risk_scores.infectious >= 70,
    ).length,
  }
}
