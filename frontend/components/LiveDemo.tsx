"use client";

import Link from "next/link";
import { Check, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { ReadinessGauge } from "@/components/ReadinessGauge";
import { ALL_SKILLS, priorityFor, ROLE_DEFINITIONS } from "@/lib/roles";
import { scoreRole } from "@/lib/scoring";

const STARTER_SKILLS = ["Python", "SQL", "Git", "JavaScript"];
const VISIBLE_ROLES = ROLE_DEFINITIONS.slice(0, 5);
const EXTRA_ROLES = ROLE_DEFINITIONS.slice(5);
const DEMO_SCENARIOS = [
  ["Python", "SQL", "Git", "JavaScript"],
  ["Python", "SQL", "Git", "REST APIs", "PostgreSQL"],
  ["JavaScript", "React", "TypeScript", "HTML", "CSS", "Git"],
];

const segmentLabels = {
  skill_match: "Skills",
  project_evidence: "Projects",
  experience: "Experience",
  education: "Education",
  interest: "Interest",
} as const;

export function LiveDemo() {
  const [roleName, setRoleName] = useState("Backend Developer");
  const [selectedSkills, setSelectedSkills] = useState<string[]>(STARTER_SKILLS);
  const [hasInteracted, setHasInteracted] = useState(false);
  const [scenarioIndex, setScenarioIndex] = useState(0);

  useEffect(() => {
    if (hasInteracted) return undefined;
    const timer = window.setInterval(() => {
      setScenarioIndex((current) => (current + 1) % DEMO_SCENARIOS.length);
    }, 5200);
    return () => window.clearInterval(timer);
  }, [hasInteracted]);

  useEffect(() => {
    if (!hasInteracted) setSelectedSkills(DEMO_SCENARIOS[scenarioIndex]);
  }, [scenarioIndex, hasInteracted]);

  const role = useMemo(
    () => ROLE_DEFINITIONS.find((item) => item.name === roleName) ?? ROLE_DEFINITIONS[0],
    [roleName]
  );
  const selectedSet = useMemo(() => new Set(selectedSkills), [selectedSkills]);
  const totalWeight = Object.values(role.skills).reduce((total, importance) => total + importance, 0);
  const matchedWeight = Object.entries(role.skills).reduce(
    (total, [skill, importance]) => total + (selectedSet.has(skill) ? importance : 0),
    0
  );
  const skillMatch = totalWeight === 0 ? 0 : (matchedWeight / totalWeight) * 100;
  const empty = selectedSkills.length === 0;
  const result = empty
    ? { matchPercent: 0, breakdown: { skill_match: 0, project_evidence: 0, experience: 0, education: 0, interest: 0 } }
    : scoreRole(skillMatch);
  const missing = Object.entries(role.skills)
    .filter(([skill]) => !selectedSet.has(skill))
    .sort(([, left], [, right]) => right - left);
  const suggestedSkills = missing.slice(0, 2).map(([skill]) => skill);
  const projectedSkills = new Set([...selectedSkills, ...suggestedSkills]);
  const projectedWeight = Object.entries(role.skills).reduce(
    (total, [skill, importance]) => total + (projectedSkills.has(skill) ? importance : 0),
    0
  );
  const projected = selectedSkills.length === 0
    ? 0
    : scoreRole((projectedWeight / totalWeight) * 100).matchPercent;

  function toggleSkill(skill: string) {
    setHasInteracted(true);
    setSelectedSkills((current) => current.includes(skill)
      ? current.filter((item) => item !== skill)
      : [...current, skill]);
  }

  function selectRole(name: string) {
    setHasInteracted(true);
    setRoleName(name);
  }

  return (
    <section className="instrument-panel" aria-label="Interactive CareerOS scoring demo">
      <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cobalt-light">Live scoring engine</p>
          <p className="mt-1 text-sm text-slate-light">Choose a role and skills you already have.</p>
        </div>
        <span className="flex shrink-0 items-center gap-1.5 text-xs text-cobalt-light"><Sparkles size={13} /> live</span>
      </div>

      <div className="mt-5 flex flex-wrap gap-2" aria-label="Select a target role">
        {VISIBLE_ROLES.map((item) => (
          <button key={item.name} type="button" onClick={() => selectRole(item.name)} className={`demo-role-tab ${roleName === item.name ? "demo-role-tab-active" : ""}`}>
            {item.name.replace(" Developer", "")}
          </button>
        ))}
        <select value={EXTRA_ROLES.some((item) => item.name === roleName) ? roleName : ""} onChange={(event) => event.target.value && selectRole(event.target.value)} className="demo-role-select" aria-label="More career options">
          <option value="" disabled>More careers</option>
          {EXTRA_ROLES.map((item) => <option key={item.name} value={item.name}>{item.name}</option>)}
        </select>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <div>
          <div className="flex items-center justify-between gap-3"><p className="text-xs font-semibold uppercase tracking-[0.14em] text-slate-light">Your current skills</p><button type="button" onClick={() => { setHasInteracted(true); setSelectedSkills([]); }} disabled={empty} className="demo-clear-button">Unselect all</button></div>
          <div className="demo-skill-scroller mt-3" aria-label="Toggle your skills">
            {ALL_SKILLS.map((skill) => {
              const active = selectedSet.has(skill);
              return <button key={skill} type="button" onClick={() => toggleSkill(skill)} className={`demo-skill-chip ${active ? "demo-skill-chip-active" : ""}`} aria-pressed={active}>
                {active && <Check size={13} strokeWidth={3} />} {skill}
              </button>;
            })}
          </div>
          {!hasInteracted && <p className="mt-3 text-xs text-slate-light">Demo inputs refresh every few seconds. Choose a chip to take control.</p>}
        </div>

        <div className="rounded-xl border border-white/10 bg-white/[0.035] px-4 py-5">
          <div className="flex justify-center"><ReadinessGauge value={result.matchPercent} size={188} /></div>
          <p className="mt-1 text-center text-xs text-slate-light">{empty ? "Select skills to calculate your match." : `Computed for ${role.name}`}</p>
          <div className="mt-5">
            <div className="mb-2 flex items-center justify-between text-xs text-slate-light"><span>Auditable score breakdown</span><span className="tabular-nums">{result.matchPercent}%</span></div>
            <div className="flex h-3 overflow-hidden rounded-full bg-white/10" aria-label="Score contribution breakdown">
              {Object.entries(result.breakdown).map(([key, value]) => value > 0 && <span key={key} title={`${segmentLabels[key as keyof typeof segmentLabels]}: ${value}%`} className={`score-segment score-segment-${key}`} style={{ width: `${value}%` }} />)}
            </div>
            <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-slate-light">
              {Object.entries(result.breakdown).map(([key, value]) => <span key={key}><span className="tabular-nums text-white">{value}%</span> {segmentLabels[key as keyof typeof segmentLabels]}</span>)}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 border-t border-white/10 pt-4">
        <div className="flex flex-wrap items-center justify-between gap-2"><p className="text-sm font-medium text-white">Top gaps to work on</p><span className="text-xs text-slate-light">ordered by role importance</span></div>
        <div className="mt-3 flex flex-wrap gap-2">
          {missing.slice(0, 3).map(([skill, importance]) => <span key={skill} className={`demo-gap demo-gap-${priorityFor(importance).toLowerCase()}`}>{skill} <b>{priorityFor(importance)}</b></span>)}
          {missing.length === 0 && <span className="text-sm text-cobalt-light">All role skills selected — excellent coverage.</span>}
        </div>
        {!empty && suggestedSkills.length > 0 && <p className="mt-4 text-sm leading-6 text-slate-light">Add <span className="font-medium text-white">{suggestedSkills.join(" and ")}</span> and your {role.name} match moves from <span className="tabular-nums text-white">{result.matchPercent}%</span> to <span className="tabular-nums text-white">{projected}%</span>.</p>}
      </div>

      <p className="mt-5 border-t border-white/10 pt-4 text-xs leading-5 text-slate-light">Demo mode uses baseline values for projects, experience, education and interest; the full version derives these from your resume. <Link href="/signup" className="text-cobalt-light underline underline-offset-2">Sign up to run it on your actual resume.</Link></p>
    </section>
  );
}
