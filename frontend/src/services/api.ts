import axios from 'axios'
import {
  buildMockConsultationResult,
  buildMockSimulation,
  getMockPatientTimeline,
  mockDashboardStats,
  mockPatients,
  mockWeeklyConsultations,
} from '../mocks/data'
import {
  type ConsultationPayload,
  type ConsultationResult,
  type DashboardStats,
  type Patient,
  type PatientTimelineResponse,
  type SimulationPayload,
  type SimulationResponse,
  type WeeklyConsultationStat,
} from '../types'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
    typeof record.treatment_hypothesis === 'string' &&
    Array.isArray(record.trajectory)
  )
}

export const submitConsultation = async (
  payload: ConsultationPayload,
): Promise<ConsultationResult> => {
  try {
    const response = await api.post<unknown>('/consultation', payload)
    if (isConsultationResult(response.data)) {
      return response.data
    }
    return buildMockConsultationResult(payload)
  } catch {
    return buildMockConsultationResult(payload)
  }
}

export const getPatientTimeline = async (
  patientId: string,
): Promise<PatientTimelineResponse> => {
  try {
    const response = await api.get<unknown>(`/patient/${patientId}/timeline`)
    if (isPatientTimelineResponse(response.data)) {
      return response.data
    }
    return getMockPatientTimeline(patientId)
  } catch {
    return getMockPatientTimeline(patientId)
  }
}

export const simulateTreatment = async (
  payload: SimulationPayload,
): Promise<SimulationResponse> => {
  try {
    const response = await api.post<unknown>('/simulate-treatment', payload)
    if (isSimulationResponse(response.data)) {
      return response.data
    }
    return buildMockSimulation(payload)
  } catch {
    return buildMockSimulation(payload)
  }
}

export const getRecentPatients = async (): Promise<Patient[]> => {
  return Promise.resolve(mockPatients)
}

export const getWeeklyConsultations = async (): Promise<WeeklyConsultationStat[]> => {
  return Promise.resolve(mockWeeklyConsultations)
}

export const getDashboardStats = async (): Promise<DashboardStats> => {
  return Promise.resolve(mockDashboardStats)
}
