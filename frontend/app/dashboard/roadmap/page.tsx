"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Circle } from "lucide-react";
import { api } from "@/lib/api";
import { Topbar } from "@/components/Topbar";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { RoadmapPlan } from "@/lib/types";
import { ROLE_DEFINITIONS } from "@/lib/roles";

const ROLES = ROLE_DEFINITIONS.map((role) => role.name);

export default function RoadmapPage() {
  const [role, setRole] = useState(ROLES[0]);
  const [roadmap, setRoadmap] = useState<RoadmapPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [weeks, setWeeks] = useState(8);

  function loadExisting(r: string) {
    setLoading(true);
    api.get<RoadmapPlan>(`/api/roadmap/${encodeURIComponent(r)}`)
      .then(setRoadmap)
      .catch(() => setRoadmap(null))
      .finally(() => setLoading(false));
  }

  useEffect(() => { loadExisting(role); }, [role]);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const plan = await api.post<RoadmapPlan>("/api/roadmap/generate", { role_name: role, total_weeks: weeks });
      setRoadmap(plan);
    } finally {
      setGenerating(false);
    }
  }

  async function toggleItem(id: number) {
    await api.patch(`/api/roadmap/item/${id}/toggle`);
    loadExisting(role);
  }

  return (
    <div>
      <Topbar title="Roadmap" subtitle="A week-by-week plan built from your actual skill gaps." />

      <div className="flex gap-2 mb-6 flex-wrap items-center">
        {ROLES.map((r) => (
          <button
            key={r}
            onClick={() => setRole(r)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              role === r ? "bg-ink text-white" : "bg-black/5 text-slate hover:bg-black/10"
            }`}
          >
            {r}
          </button>
        ))}
        <Button variant="secondary" onClick={handleGenerate} disabled={generating} className="ml-auto">
          {generating ? "Generating..." : roadmap ? "Regenerate" : "Generate roadmap"}
        </Button>
      </div>
      <Card className="mb-6"><p className="font-medium">Choose your pace</p><p className="mt-1 text-sm text-slate">Shorter timelines keep all topics but require more study hours each week.</p><div className="mt-4 flex flex-wrap gap-2">{[4, 8, 12, 16].map((value) => <button key={value} onClick={() => setWeeks(value)} className={`rounded-md px-4 py-2 text-sm font-medium ${weeks === value ? "bg-cobalt text-white" : "border border-black/10 text-slate"}`}>{value} weeks · {{ 4: 18, 8: 10, 12: 7, 16: 5 }[value as 4 | 8 | 12 | 16]} hrs/week</button>)}</div></Card>

      {loading && <p className="text-slate">Loading...</p>}

      {!loading && !roadmap && (
        <p className="text-slate">No roadmap yet for {role}. Generate one above.</p>
      )}

      {!loading && roadmap && (
        <div className="space-y-4">
          <Card className="border-cobalt/30"><p className="font-medium">Your {roadmap.total_weeks}-week plan</p><p className="mt-1 text-sm text-slate">Recommended pace: <b className="text-ink">{roadmap.weekly_study_hours} hours each week</b>. {roadmap.total_weeks <= 4 ? "This is an intensive schedule." : roadmap.total_weeks >= 16 ? "This is a relaxed, sustainable schedule." : "Keep this pace consistently to finish on time."}</p></Card>
          {roadmap.items.map((item) => (
            <Card key={item.week_number}>
              <div className="flex items-start gap-4">
                <button onClick={() => toggleItem(item.id)} className="mt-1">
                  {item.completed ? (
                    <CheckCircle2 size={20} className="text-gold" />
                  ) : (
                    <Circle size={20} className="text-slate" />
                  )}
                </button>
                <div className="flex-1">
                  <div className="flex items-baseline justify-between">
                    <h3 className="font-display font-semibold">
                      Week {item.week_number} — {item.topic}
                    </h3>
                    <span className="text-xs text-slate">{item.estimated_days} days</span>
                  </div>
                  <p className="text-sm text-slate mt-1">{item.why_needed}</p>
                  <div className="mt-4 rounded-md border border-black/10 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wide text-cobalt mb-3">Study structure</p>
                    <ol className="grid gap-2 text-sm sm:grid-cols-2">
                      {(item.subtopics ?? []).map((subtopic, index) => <li key={subtopic} className="flex gap-2"><span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-cobalt-light text-xs font-semibold text-cobalt-dark">{index + 1}</span><span>{subtopic}</span></li>)}
                    </ol>
                  </div>
                  <div className="grid md:grid-cols-2 gap-3 mt-3 text-sm">
                    <div className="roadmap-practice-card rounded-md p-3">
                      <p className="text-xs font-medium text-cobalt-dark mb-1">Practice task</p>
                      <p>{item.practice_task}</p>
                    </div>
                    <div className="roadmap-project-card rounded-md p-3">
                      <p className="text-xs font-medium text-cobalt mb-1">Portfolio evidence</p>
                      <p>{item.project_suggestion}</p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
