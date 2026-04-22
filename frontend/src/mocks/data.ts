import {
  type ConsultationPayload,
  type ConsultationResult,
  type DashboardStats,
  type Patient,
  type PatientTimelineResponse,
  type RiskItem,
  type SimulationPayload,
  type SimulationResponse,
  type TimelineEvent,
  type VitalsPoint,
  type WeeklyConsultationStat,
} from '../types'

const dayMillis = 24 * 60 * 60 * 1000

const toISODate = (date: Date): string => date.toISOString().slice(0, 10)

const buildVitalsSeries = (
  start: Date,
  baseline: {
    systolic: number
    diastolic: number
    heartRate: number
    weight: number
    glucose: number
    temperature: number
  },
): VitalsPoint[] => {
  return Array.from({ length: 30 }, (_, index) => {
    const date = new Date(start.getTime() + index * dayMillis)
    return {
      date: toISODate(date),
      systolic: baseline.systolic + Math.round(Math.sin(index / 4) * 6 + ((index % 3) - 1)),
      diastolic: baseline.diastolic + Math.round(Math.cos(index / 5) * 4),
      heart_rate: baseline.heartRate + Math.round(Math.sin(index / 3) * 5),
      weight: Number((baseline.weight + Math.sin(index / 9) * 0.8).toFixed(1)),
      glucose: baseline.glucose + Math.round(Math.cos(index / 6) * 10 + (index % 4)),
      temperature: Number((baseline.temperature + Math.sin(index / 7) * 0.3).toFixed(1)),
    }
  })
}

export const mockPatients: Patient[] = [
  {
    id: 'PT-1001',
    name: 'Marie Dubois',
    age: 67,
    comorbidities: ['HTA', 'Diabete type 2'],
    current_treatment: 'Metformine 850 mg x2, Ramipril 5 mg',
    active_alerts: 2,
    last_consultation: '2026-04-20',
    risk_scores: { cardio: 78, metabolic: 73, infectious: 28 },
  },
  {
    id: 'PT-1002',
    name: 'Karim Benali',
    age: 54,
    comorbidities: ['Dyslipidemie'],
    current_treatment: 'Atorvastatine 20 mg',
    active_alerts: 1,
    last_consultation: '2026-04-19',
    risk_scores: { cardio: 46, metabolic: 52, infectious: 18 },
  },
  {
    id: 'PT-1003',
    name: 'Sophie Martin',
    age: 43,
    comorbidities: ['Asthme'],
    current_treatment: 'Budesonide/Formoterol inhalation',
    active_alerts: 0,
    last_consultation: '2026-04-18',
    risk_scores: { cardio: 24, metabolic: 29, infectious: 41 },
  },
]

const seriesByPatient: Record<string, VitalsPoint[]> = {
  'PT-1001': buildVitalsSeries(new Date('2026-03-22'), {
    systolic: 146,
    diastolic: 91,
    heartRate: 82,
    weight: 82,
    glucose: 172,
    temperature: 36.9,
  }),
  'PT-1002': buildVitalsSeries(new Date('2026-03-22'), {
    systolic: 134,
    diastolic: 86,
    heartRate: 76,
    weight: 89,
    glucose: 138,
    temperature: 36.7,
  }),
  'PT-1003': buildVitalsSeries(new Date('2026-03-22'), {
    systolic: 124,
    diastolic: 80,
    heartRate: 74,
    weight: 68,
    glucose: 112,
    temperature: 36.8,
  }),
}

const timelineByPatient: Record<string, TimelineEvent[]> = {
  'PT-1001': [
    {
      id: 'evt-1',
      date: '2026-04-20',
      type: 'alert',
      title: 'Alerte glycemie elevee',
      details: 'Glycemie capillaire > 180 mg/dL sur 3 jours consecutifs',
      severity: 'high',
    },
    {
      id: 'evt-2',
      date: '2026-04-18',
      type: 'note',
      title: 'Controle trimestriel',
      details: 'Fatigue matinale signalee, adherence traitement correcte',
      severity: 'medium',
    },
    {
      id: 'evt-3',
      date: '2026-04-16',
      type: 'prescription',
      title: 'Ajustement antihypertenseur',
      details: 'Ramipril augmente de 2.5 mg a 5 mg',
    },
  ],
  'PT-1002': [
    {
      id: 'evt-4',
      date: '2026-04-19',
      type: 'note',
      title: 'Suivi lipidique',
      details: 'LDL en baisse, poursuite traitement actuel',
      severity: 'low',
    },
    {
      id: 'evt-5',
      date: '2026-04-13',
      type: 'alert',
      title: 'TA intermittente elevee',
      details: 'Pics systoliques > 140 mmHg en fin de journee',
      severity: 'medium',
    },
    {
      id: 'evt-6',
      date: '2026-04-09',
      type: 'prescription',
      title: 'Plan activite physique',
      details: 'Marche rapide 30 min, 5 jours/semaine',
    },
  ],
  'PT-1003': [
    {
      id: 'evt-7',
      date: '2026-04-18',
      type: 'note',
      title: 'Suivi asthme',
      details: 'Dyspnee legere a l effort, pas de crise recente',
      severity: 'low',
    },
    {
      id: 'evt-8',
      date: '2026-04-12',
      type: 'alert',
      title: 'Episode infectieux possible',
      details: 'Toux productive et temperature a 37.8 degres',
      severity: 'medium',
    },
    {
      id: 'evt-9',
      date: '2026-04-10',
      type: 'prescription',
      title: 'Renouvellement traitement inhalation',
      details: 'Budesonide/Formoterol pour 3 mois',
    },
  ],
}

export const mockWeeklyConsultations: WeeklyConsultationStat[] = [
  { week: 'S-5', consultations: 14 },
  { week: 'S-4', consultations: 17 },
  { week: 'S-3', consultations: 19 },
  { week: 'S-2', consultations: 16 },
  { week: 'S-1', consultations: 22 },
  { week: 'Cette semaine', consultations: 11 },
]

export const mockDashboardStats: DashboardStats = {
  consultations_today: 9,
  active_alerts: mockPatients.reduce((sum, patient) => sum + patient.active_alerts, 0),
  high_risk_patients: mockPatients.filter((patient) => patient.risk_scores.cardio >= 70 || patient.risk_scores.metabolic >= 70).length,
}

export const getMockPatientTimeline = (patientId: string): PatientTimelineResponse => {
  const patient = mockPatients.find((item) => item.id === patientId) ?? mockPatients[0]
  return {
    patient,
    timeline: timelineByPatient[patient.id] ?? [],
    vitals_series: seriesByPatient[patient.id] ?? [],
    risk_scores: patient.risk_scores,
  }
}

const buildRiskList = (payload: ConsultationPayload): RiskItem[] => {
  const risks: RiskItem[] = []
  if (payload.vitals.systolic >= 140 || payload.vitals.diastolic >= 90) {
    risks.push({
      label: 'Risque cardiovasculaire',
      level: 'high',
      score: 82,
      reason: 'Tension arterielle persistante au-dessus des cibles',
    })
  }
  if (payload.vitals.glucose >= 160) {
    risks.push({
      label: 'Desequilibre metabolique',
      level: 'medium',
      score: 68,
      reason: 'Hyperglycemie a surveiller sur les prochaines 72h',
    })
  }
  if (payload.vitals.temperature >= 37.8) {
    risks.push({
      label: 'Risque infectieux',
      level: 'medium',
      score: 57,
      reason: 'Temperature elevee avec contexte clinique compatible',
    })
  }

  if (risks.length === 0) {
    risks.push({
      label: 'Stabilite clinique',
      level: 'low',
      score: 22,
      reason: 'Aucun signal de decompensation immediate detecte',
    })
  }

  return risks
}

export const buildMockConsultationResult = (payload: ConsultationPayload): ConsultationResult => {
  const risks = buildRiskList(payload)
  return {
    structured_summary:
      `Consultation de ${payload.patient_id}. Parametres principaux: TA ${payload.vitals.systolic}/${payload.vitals.diastolic} mmHg, FC ${payload.vitals.heart_rate} bpm, glycemie ${payload.vitals.glucose} mg/dL.`,
    prioritized_risks: risks,
    suggested_questions: [
      'Avez-vous constate des symptomes nouveaux depuis la derniere consultation ?',
      'Le traitement est-il pris regulierement aux horaires prevus ?',
      'Comment evoluent votre alimentation et votre niveau d activite physique cette semaine ?',
    ],
  }
}

export const buildMockSimulation = (payload: SimulationPayload): SimulationResponse => {
  const baseline = getMockPatientTimeline(payload.patient_id).vitals_series.slice(-1)[0]
  const startingRisk = Math.max(
    25,
    Math.min(90, Math.round((baseline.systolic - 110) * 0.8 + (baseline.glucose - 90) * 0.2)),
  )

  const trajectory = Array.from({ length: 14 }, (_, index) => {
    const progression = Math.max(0, startingRisk - index * 2 + Math.round(Math.sin(index / 2) * 2))
    return {
      day: `J+${index + 1}`,
      risk_index: progression,
      systolic: Math.max(110, baseline.systolic - index),
      glucose: Math.max(95, baseline.glucose - Math.round(index * 1.5)),
    }
  })

  return {
    patient_id: payload.patient_id,
    treatment_hypothesis: payload.treatment_hypothesis,
    trajectory,
  }
}
