export type RiskLevel = 'low' | 'medium' | 'high'

export interface RiskItem {
  label: string
  level: RiskLevel
  score: number
  reason: string
}

export interface RiskScores {
  cardio: number
  metabolic: number
  infectious: number
}

export interface Vitals {
  systolic: number
  diastolic: number
  heart_rate: number
  weight: number
  glucose: number
  temperature: number
}

export interface ConsultationPayload {
  patient_id: string
  note_text: string
  vitals: Vitals
  image?: string
}

export interface ConsultationResult {
  structured_summary: string
  prioritized_risks: RiskItem[]
  suggested_questions: string[]
}

export type TimelineEventType = 'note' | 'alert' | 'prescription'

export interface TimelineEvent {
  id: string
  date: string
  type: TimelineEventType
  title: string
  details: string
  severity?: RiskLevel
}

export interface VitalsPoint {
  date: string
  systolic: number
  diastolic: number
  heart_rate: number
  weight: number
  glucose: number
  temperature: number
}

export interface Patient {
  id: string
  name: string
  age: number
  comorbidities: string[]
  current_treatment: string
  active_alerts: number
  last_consultation: string
  risk_scores: RiskScores
}

export interface PatientTimelineResponse {
  patient: Patient
  timeline: TimelineEvent[]
  vitals_series: VitalsPoint[]
  risk_scores: RiskScores
}

export interface WeeklyConsultationStat {
  week: string
  consultations: number
}

export interface DashboardStats {
  consultations_today: number
  active_alerts: number
  high_risk_patients: number
}

export interface SimulationPayload {
  patient_id: string
  treatment_hypothesis: string
}

export interface SimulationPoint {
  day: string
  risk_index: number
  systolic: number
  glucose: number
}

export interface SimulationResponse {
  patient_id: string
  treatment_hypothesis: string
  trajectory: SimulationPoint[]
}
