"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import clsx from "clsx";
import {
  LayoutDashboard, FileText, Target, Puzzle, Map, Briefcase, LogOut, Settings, PenLine,
} from "lucide-react";
import { clearToken } from "@/lib/auth";

const links = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/resume", label: "Resume Analyzer", icon: FileText },
  { href: "/dashboard/resume-builder", label: "Resume Builder", icon: PenLine },
  { href: "/dashboard/career-match", label: "Career Match", icon: Target },
  { href: "/dashboard/skill-gap", label: "Skill Gap", icon: Puzzle },
  { href: "/dashboard/roadmap", label: "Roadmap", icon: Map },
  { href: "/dashboard/jobs", label: "JD Analyzer", icon: Briefcase },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <aside className="w-64 shrink-0 border-r border-black/[0.06] bg-surface min-h-screen flex flex-col">
      <div className="px-6 py-6 border-b border-black/[0.06]">
        <span className="font-display text-xl font-semibold">CareerOS</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors",
                active ? "bg-cobalt-light text-cobalt-dark" : "text-slate hover:bg-black/5 hover:text-ink"
              )}
            >
              <Icon size={18} strokeWidth={2} />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="px-3 py-4 border-t border-black/[0.06]">
        <button
          onClick={() => {
            clearToken();
            router.push("/login");
          }}
          className="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium text-slate hover:bg-black/5 hover:text-ink w-full"
        >
          <LogOut size={18} strokeWidth={2} />
          Log out
        </button>
      </div>
    </aside>
  );
}
