export interface User {
  id: number;
  email: string;
  full_name: string | null;
  college: string | null;
  degree: string | null;
  branch: string | null;
  graduation_year: number | null;
  target_role: string | null;
  experience_level: string | null;
}

export interface BulletRewrite {
  before: string;
  after: string;
}

export interface ResumeAnalysis {
  overall_score: number;
  ats_score: number;
  category_scores: Record<string, number>;
  parsed_profile: Record<string, unknown>;
  strengths: string[];
  weaknesses: string[];
  bullet_rewrites: BulletRewrite[];
}

export interface Resume {
  id: number;
  filename: string;
  analysis: ResumeAnalysis | null;
}

export interface RoleMatch {
  role_name: string;
  match_percent: number;
  breakdown: Record<string, number>;
  base_match_percent?: number;
}

export interface SkillGapItem {
  skill: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  user_level: number;
  required_level: number;
  status: "missing" | "developing";
}

export interface SkillGap {
  role_name: string;
  matched_skills: string[];
  gaps: SkillGapItem[];
}

export interface DashboardSummary {
  status: "ok" | "no_data";
  readiness?: { match_percent: number; role_name: string };
  top_gaps?: SkillGapItem[];
  roadmap_progress?: { completed_weeks: number; total_weeks: number; role_name: string } | null;
  resume_status: { uploaded: boolean; overall_score?: number; source?: "upload" | "builder" | "none" };
}

export interface UserSkill { skill_name: string; proficiency: number; evidence_source?: string; }

export interface RoadmapItem {
  id: number;
  week_number: number;
  topic: string;
  why_needed: string | null;
  current_level: string | null;
  target_level: string | null;
  estimated_days: number;
  practice_task: string | null;
  project_suggestion: string | null;
  subtopics: string[] | null;
  resources: string | null;
  completed: boolean;
}

export interface RoadmapPlan {
  id: number;
  role_name: string;
  total_weeks: number;
  items: RoadmapItem[];
  weekly_study_hours: number;
}

export interface JDAnalysis {
  id: number;
  title: string | null;
  extracted_skills: string[];
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  requirement_breakdown: { label: string; status: "matched" | "partial" | "missing"; weight: number; evidence: string }[];
  recommendation: string | null;
}
