import Link from "next/link";
import { ArrowRight, BriefcaseBusiness, FileText, Map, Puzzle, ScanSearch, Target } from "lucide-react";
import { LiveDemo } from "@/components/LiveDemo";
import { PublicNav } from "@/components/PublicNav";
import { Reveal } from "@/components/Reveal";

const loop = [
  { icon: FileText, title: "Resume", body: "Turn your document into structured evidence." },
  { icon: Target, title: "Profile", body: "Build a measurable view of your current skills." },
  { icon: Puzzle, title: "Skill Gap", body: "Compare evidence against a role's requirements." },
  { icon: Map, title: "Roadmap", body: "Convert missing skills into practical weekly work." },
  { icon: ScanSearch, title: "Readiness", body: "Track progress and recalculate the next priority." },
];

const features = [
  { icon: ScanSearch, title: "Resume analysis that reads like a hiring manager", body: "Category scores, ATS compatibility, and line-by-line bullet rewrites give you specific next edits.", wide: true },
  { icon: Target, title: "Career matching you can audit", body: "Skills 50%, project evidence 20%, experience 15%, interest 10%, education 5%." },
  { icon: Puzzle, title: "Skill gaps ranked by priority", body: "HIGH, MEDIUM and LOW gaps make the learning order clear for your target role." },
  { icon: Map, title: "A roadmap tied to outcomes", body: "Every topic includes why it matters, a practice task, and a project idea." },
  { icon: BriefcaseBusiness, title: "Job descriptions matched against you", body: "Paste a JD, see your match, and find the exact skills still missing." },
];

export default function LandingPage() {
  return <main className="overflow-hidden bg-paper">
    <PublicNav />
    <section className="hero-canvas relative pt-28 text-white lg:pt-36">
      <div className="mx-auto grid max-w-7xl gap-12 px-5 pb-16 sm:px-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-center lg:pb-32">
        <div className="relative z-10 max-w-2xl">
          <span className="inline-flex rounded-full border border-white/15 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.16em] text-cobalt-light">AI career intelligence</span>
          <h1 className="mt-7 font-display text-[clamp(2.75rem,6vw,4.5rem)] font-semibold leading-[1.05] tracking-[-0.045em]">Know where you stand. Know where you&apos;re going.</h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-light">CareerOS connects your resume, role fit, skill gaps and roadmap into one measurable plan—not a pile of disconnected advice.</p>
          <div className="mt-8 flex flex-wrap gap-3"><Link href="/signup" className="inline-flex items-center gap-2 rounded-md bg-cobalt px-5 py-3 font-medium text-white transition hover:bg-cobalt-dark">Analyze my resume <ArrowRight size={17} /></Link><a href="#how-it-works" className="inline-flex items-center gap-2 rounded-md border border-white/15 px-5 py-3 font-medium transition hover:bg-white/5">See how it works <ArrowRight size={17} /></a></div>
          <div className="mt-11 grid max-w-lg grid-cols-3 divide-x divide-white/10 border-y border-white/10 py-4 text-sm"><div className="pr-4"><strong className="block tabular-nums text-xl text-white">13</strong><span className="text-slate-light">career paths</span></div><div className="px-4"><strong className="block tabular-nums text-xl text-white">5</strong><span className="text-slate-light">score inputs</span></div><div className="pl-4"><strong className="block tabular-nums text-xl text-white">4-16 wk</strong><span className="text-slate-light">roadmap pace</span></div></div>
        </div>
        <div className="relative z-10"><LiveDemo /></div>
      </div>
    </section>

    <section id="how-it-works" className="relative mx-auto max-w-7xl px-5 py-20 sm:px-8 lg:-mt-12 lg:py-28">
      <Reveal><p className="eyebrow">The CareerOS loop</p><h2 className="section-title mt-3">One connected system, not five disconnected tools.</h2><p className="mt-4 max-w-2xl text-lg leading-8 text-slate">Most tools stop after one answer. CareerOS feeds each output into the next decision, then recalculates as you make progress.</p></Reveal>
      <Reveal className="relative mt-12"><div className="loop-grid">{loop.map(({ icon: Icon, title, body }, index) => <article key={title} className="loop-node"><span className="flex h-10 w-10 items-center justify-center rounded-md bg-cobalt-light text-cobalt"><Icon size={19} /></span><p className="mt-5 font-display text-lg font-semibold">{title}</p><p className="mt-2 text-sm leading-6 text-slate">{body}</p>{index < loop.length - 1 && <ArrowRight className="loop-arrow" size={19} />}</article>)}</div><svg className="loop-return" viewBox="0 0 300 74" fill="none" aria-hidden="true"><path d="M280 6C260 75 35 75 15 19" stroke="#3652FF" strokeWidth="1.5" strokeDasharray="4 5"/><path d="M10 28L15 17L25 24" stroke="#3652FF" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg></Reveal>
    </section>

    <section id="features" className="border-y border-black/[0.06] bg-surface"><div className="mx-auto max-w-7xl px-5 py-20 sm:px-8 lg:py-28"><Reveal><p className="eyebrow">What it measures</p><h2 className="section-title mt-3">Useful signals, connected to a next step.</h2></Reveal><div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-3">{features.map(({ icon: Icon, title, body, wide }) => <Reveal key={title} className={wide ? "md:col-span-2 lg:row-span-2" : ""}><article className="feature-tile h-full"><span className="flex h-11 w-11 items-center justify-center rounded-md bg-cobalt-light text-cobalt"><Icon size={21} /></span><h3 className="mt-7 font-display text-xl font-semibold">{title}</h3><p className="mt-3 max-w-md leading-7 text-slate">{body}</p>{title.includes("audit") && <div className="mt-8 flex h-3 overflow-hidden rounded-full"><span className="w-1/2 bg-cobalt"/><span className="w-1/5 bg-cobalt/75"/><span className="w-[15%] bg-cobalt/55"/><span className="w-[10%] bg-cobalt/35"/><span className="w-[5%] bg-cobalt/20"/></div>}</article></Reveal>)}</div></div></section>

    <section className="bg-ink"><div className="mx-auto max-w-7xl px-5 py-12 sm:px-8"><p className="max-w-3xl font-display text-2xl font-semibold leading-snug text-white">No number on CareerOS comes from a black box. Every score can be traced to the evidence and weights behind it.</p><div className="mt-7 flex h-4 overflow-hidden rounded-full text-[10px] font-semibold text-white"><span className="flex w-1/2 items-center justify-center bg-cobalt">Skills 50%</span><span className="flex w-1/5 items-center justify-center bg-cobalt/80">Projects 20%</span><span className="flex w-[15%] items-center justify-center bg-cobalt/65">15%</span><span className="flex w-[10%] items-center justify-center bg-cobalt/50">10%</span><span className="flex w-[5%] items-center justify-center bg-cobalt/35">5%</span></div><div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-light"><span>Experience 15%</span><span>Interest 10%</span><span>Education 5%</span></div></div></section>

    <section className="mx-auto max-w-4xl px-5 py-24 text-center sm:px-8"><Reveal><p className="eyebrow">Start with the evidence</p><h2 className="section-title mt-3">Turn your current profile into a plan you can act on.</h2><Link href="/signup" className="mt-8 inline-flex items-center gap-2 rounded-md bg-ink px-5 py-3 font-medium text-white transition hover:bg-cobalt">Get started <ArrowRight size={17} /></Link><p className="mt-4 text-sm text-slate">Free to use. No credit card.</p></Reveal></section>

    <footer className="border-t border-black/[0.06] bg-surface"><div className="mx-auto grid max-w-7xl gap-10 px-5 py-12 sm:px-8 md:grid-cols-[2fr_1fr_1fr_1fr]"><div><p className="font-display text-xl font-semibold">CareerOS</p><p className="mt-3 max-w-xs text-sm leading-6 text-slate">Analyze. Discover. Upskill. Get Career-Ready.</p></div>{[["Product", "Features", "How it works", "Roadmap"], ["Resources", "Help center", "Career guides", "Status"], ["Legal", "Privacy", "Terms", "Contact"]].map(([heading, ...links]) => <div key={heading}><p className="text-sm font-semibold">{heading}</p>{links.map((item) => <a key={item} href="#" className="mt-3 block text-sm text-slate hover:text-cobalt">{item}</a>)}</div>)}</div><div className="mx-auto max-w-7xl border-t border-black/[0.06] px-5 py-5 text-xs text-slate sm:px-8">© {new Date().getFullYear()} CareerOS. Built for clear career decisions.</div></footer>
  </main>;
}
