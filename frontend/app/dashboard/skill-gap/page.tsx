"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Topbar } from "@/components/Topbar";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { SkillGap, User } from "@/lib/types";
import { ROLE_DEFINITIONS } from "@/lib/roles";

const ROLES = ROLE_DEFINITIONS.map((role) => role.name);

const toneMap = { HIGH: "high", MEDIUM: "medium", LOW: "low" } as const;

export default function SkillGapPage() {
  const [role, setRole] = useState(ROLES[0]);
  const [gap, setGap] = useState<SkillGap | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => { api.get<User>("/api/auth/me").then((user) => { if (user.target_role && ROLES.includes(user.target_role)) setRole(user.target_role); }).catch(() => undefined); }, []);

  useEffect(() => {
    setLoading(true);
    api.get<SkillGap>(`/api/skills/gap/${encodeURIComponent(role)}`)
      .then(setGap)
      .catch((caught) => { setGap(null); setError(caught instanceof Error ? caught.message : "Could not load skill gaps."); })
      .finally(() => setLoading(false));
  }, [role]);

  return (
    <div>
      <Topbar title="Skill Gap" subtitle="See exactly what's missing between you and your target role." />

      <div className="flex gap-2 mb-6 flex-wrap">
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
      </div>

      {loading && <p className="text-slate">Loading...</p>}
      {!loading && error && <Card className="border-rust/30"><p className="text-rust">{error}</p><button className="mt-2 text-sm font-medium text-cobalt underline" onClick={() => setRole(role)}>Retry</button></Card>}

      {!loading && gap && (
        <div className="space-y-6">
          <Card>
            <p className="text-sm text-slate mb-2">Skills you already have that matter for this role</p>
            <div className="flex flex-wrap gap-2">
              {gap.matched_skills.length === 0 && <span className="text-sm text-slate">None yet — add some skills first.</span>}
              {gap.matched_skills.map((s) => (
                <Badge key={s} tone="low">{s}</Badge>
              ))}
            </div>
          </Card>

          <Card>
            <p className="text-sm text-slate mb-4">Gaps, sorted by priority</p>
            <div className="space-y-3">
              {gap.gaps.length === 0 && (
                <p className="text-sm text-ink">No gaps found — you're well matched for this role.</p>
              )}
              {gap.gaps.map((g) => (
                <div key={g.skill} className={`flex items-center justify-between border-b border-black/[0.06] pb-3 last:border-0 ${g.status === "developing" ? "bg-cobalt-light/40 -mx-2 px-2 rounded" : ""}`}>
                  <div><span className="font-medium text-sm">{g.skill}</span><p className="text-xs text-slate">{g.status === "developing" ? "Developing — keep building confidence" : "Not started"}</p></div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate">{g.user_level} → {g.required_level}</span>
                    <Badge tone={toneMap[g.priority]}>{g.priority}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
