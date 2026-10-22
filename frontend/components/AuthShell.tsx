import Link from "next/link";
import { ReadinessGauge } from "@/components/ReadinessGauge";
import { SkillBar } from "@/components/SkillBar";
import { ThemeToggle } from "@/components/ThemeToggle";

export function AuthShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="min-h-screen bg-paper lg:grid lg:grid-cols-[45%_55%]">
      <aside className="auth-aside relative hidden overflow-hidden px-10 py-9 lg:flex lg:flex-col" aria-label="CareerOS product preview">
        <Link href="/" className="relative z-10 font-display text-xl font-semibold text-white">CareerOS</Link>
        <div className="relative z-10 my-auto max-w-md">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cobalt-light">Measured, not guessed</p>
          <h2 className="mt-5 font-display text-4xl font-semibold leading-tight text-white">Every career decision should show its working.</h2>
          <div className="mt-9 max-w-sm rounded-xl border border-white/10 bg-white/[0.04] p-6">
            <div className="flex justify-center"><ReadinessGauge value={72} size={165} /></div>
            <div className="mt-5 space-y-4"><SkillBar name="Python" value={82} color="cobalt" /><SkillBar name="REST APIs" value={58} color="gold" /></div>
          </div>
        </div>
        <p className="relative z-10 text-sm text-slate-light">Analyze. Discover. Upskill. Get Career-Ready.</p>
      </aside>
      <section className="relative flex min-h-screen items-center justify-center px-6 py-12 sm:px-10"><div className="absolute right-5 top-5"><ThemeToggle /></div>
        <div className="w-full max-w-[360px]">
          <Link href="/" className="font-display text-xl font-semibold text-ink lg:hidden">CareerOS</Link>
          {children}
        </div>
      </section>
    </main>
  );
}
