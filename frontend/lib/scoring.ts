// Mirrors backend/app/services/matching_service.py. Keep these weights in sync.
export const WEIGHTS = {
  skill_match: 0.5,
  project_evidence: 0.2,
  experience: 0.15,
  education: 0.05,
  interest: 0.1,
} as const;

export type ScoreBreakdown = Record<keyof typeof WEIGHTS, number>;

export function scoreRole(skillMatch: number): { matchPercent: number; breakdown: ScoreBreakdown } {
  const breakdown: ScoreBreakdown = {
    skill_match: Math.round(skillMatch * WEIGHTS.skill_match),
    project_evidence: Math.round(32 * WEIGHTS.project_evidence),
    experience: Math.round(40 * WEIGHTS.experience),
    education: Math.round(80 * WEIGHTS.education),
    interest: Math.round(60 * WEIGHTS.interest),
  };

  return { matchPercent: Object.values(breakdown).reduce((total, value) => total + value, 0), breakdown };
}
