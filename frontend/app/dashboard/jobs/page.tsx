"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Topbar } from "@/components/Topbar";
import { Card, CardLabel } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Badge } from "@/components/ui/Badge";
import { JDAnalysis } from "@/lib/types";

export default function JDAnalyzerPage() {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [result, setResult] = useState<JDAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<JDAnalysis[]>([]);

  useEffect(() => { api.get<JDAnalysis[]>("/api/jobs").then(setHistory).catch(() => []); }, []);

  async function handleAnalyze() {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const res = await api.post<JDAnalysis>("/api/jobs/analyze", { title, raw_text: text });
      setResult(res);
      setHistory((current) => [res, ...current.filter((item) => item.id !== res.id)]);
    } finally {
      setLoading(false);
    }
  }

  async function addMissingSkills() {
    if (!result) return;
    await Promise.all(result.missing_skills.map((skill) => api.post("/api/skills", { skill_name: skill, proficiency: 0, evidence_source: "jd_gap" })));
  }

  const requirementBreakdown = result?.requirement_breakdown ?? [];
  const partialRequirements = requirementBreakdown.filter((item) => item.status === "partial");

  return (
    <div>
      <Topbar title="JD Analyzer" subtitle="Paste a job description and see exactly how you match up." />

      <Card>
        <input
          placeholder="Job title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded-md border border-black/10 px-3 py-2.5 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-cobalt"
        />
        <textarea
          placeholder="Paste the full job description here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={8}
          className="w-full rounded-md border border-black/10 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-cobalt"
        />
        <Button onClick={handleAnalyze} disabled={loading} className="mt-3">
          {loading ? "Analyzing..." : "Analyze match"}
        </Button>
      </Card>

      {result && (
        <div className="mt-6 space-y-6">
          <Card>
            <CardLabel>Match score</CardLabel>
            <div className="text-3xl font-display font-semibold mb-2">{result.match_score}%</div>
            <ProgressBar value={result.match_score} color="gold" />
            {result.recommendation && (
              <p className="text-sm text-slate mt-3">{result.recommendation}</p>
            )}
          </Card>

          <Card>
            <CardLabel>Why this score</CardLabel>
            <p className="mt-2 text-sm text-slate">Each requirement is weighted from the pasted JD. Green means direct resume evidence, amber means related evidence but not an explicit claim, and red means no evidence was found.</p>
            <div className="mt-4 space-y-2">
              {requirementBreakdown.map((item) => (
                <div key={item.label} className="rounded-md border border-black/10 px-3 py-2.5">
                  <div className="flex flex-wrap items-center justify-between gap-2"><div className="flex items-center gap-2"><Badge tone={item.status === "matched" ? "low" : item.status === "partial" ? "medium" : "high"}>{item.status === "matched" ? "Strong" : item.status === "partial" ? "Partial" : "Not evidenced"}</Badge><span className="text-sm font-medium text-ink">{item.label}</span></div><span className="text-xs text-slate">{item.weight}% weight</span></div>
                  <p className="mt-1.5 text-xs text-slate">{item.evidence}</p>
                </div>
              ))}
            </div>
          </Card>

          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardLabel>Strong matches</CardLabel>
              <div className="flex flex-wrap gap-2 mt-2">
                {result.matched_skills.length === 0 && <span className="text-sm text-slate">None found.</span>}
                {result.matched_skills.map((s) => <Badge key={s} tone="low">{s}</Badge>)}
              </div>
              {result.missing_skills.length > 0 && <Button variant="secondary" onClick={addMissingSkills} className="mt-4">Add these to my target skills</Button>}
            </Card>
            <Card>
              <CardLabel>Partially matched</CardLabel>
              <div className="flex flex-wrap gap-2 mt-2">
                {partialRequirements.length === 0 && <span className="text-sm text-slate">No partial requirements.</span>}
                {partialRequirements.map((item) => <Badge key={item.label} tone="medium">{item.label}</Badge>)}
              </div>
            </Card>
            <Card>
              <CardLabel>Missing / not explicit</CardLabel>
              <div className="flex flex-wrap gap-2 mt-2">
                {result.missing_skills.length === 0 && <span className="text-sm text-slate">No missing requirements were detected.</span>}
                {result.missing_skills.map((s) => <Badge key={s} tone="high">{s}</Badge>)}
              </div>
            </Card>
          </div>
        </div>
      )}
      {history.length > 0 && <Card className="mt-6"><CardLabel>Recent JD analyses</CardLabel><div className="mt-3 space-y-2">{history.map((item) => <button key={item.id} onClick={() => setResult(item)} className="flex w-full items-center justify-between rounded-md bg-black/[0.03] px-3 py-2 text-left text-sm hover:bg-cobalt-light"><span>{item.title || "Untitled job description"}</span><span className="tabular-nums font-medium">{item.match_score}%</span></button>)}</div></Card>}
    </div>
  );
}
