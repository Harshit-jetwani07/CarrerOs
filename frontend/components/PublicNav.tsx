"use client";

import Link from "next/link";
import { Menu, X } from "lucide-react";
import { useEffect, useState } from "react";
import { ThemeToggle } from "@/components/ThemeToggle";

export function PublicNav() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const update = () => setScrolled(window.scrollY > 80);
    update(); window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);
  const navClass = scrolled ? "bg-surface/85 text-ink backdrop-blur border-black/[0.06]" : "bg-transparent text-white border-transparent";
  return <>
    <header className={`fixed inset-x-0 top-0 z-50 border-b transition-colors duration-300 ${navClass}`}>
      <nav className="mx-auto flex h-18 max-w-7xl items-center justify-between px-5 sm:px-8" aria-label="Main navigation">
        <Link href="/" className="font-display text-xl font-semibold">CareerOS</Link>
        <div className="hidden items-center gap-7 text-sm font-medium md:flex">
          <a href="#features" className="hover:text-cobalt">Features</a><a href="#how-it-works" className="hover:text-cobalt">How it works</a><Link href="/login" className="hover:text-cobalt">Log in</Link><ThemeToggle /><Link href="/signup" className="rounded-md bg-cobalt px-4 py-2.5 text-white hover:bg-cobalt-dark">Get started</Link>
        </div>
        <div className="flex items-center gap-3 md:hidden"><ThemeToggle compact /><button type="button" onClick={() => setOpen(true)} aria-label="Open navigation menu"><Menu size={24} /></button></div>
      </nav>
    </header>
    {open && <div className="fixed inset-0 z-[60] flex flex-col bg-ink px-6 py-6 text-white md:hidden">
      <div className="flex items-center justify-between"><span className="font-display text-xl font-semibold">CareerOS</span><button type="button" onClick={() => setOpen(false)} aria-label="Close navigation menu"><X size={25} /></button></div>
      <nav className="my-auto flex flex-col gap-7 font-display text-4xl" aria-label="Mobile navigation"><a href="#features" onClick={() => setOpen(false)}>Features</a><a href="#how-it-works" onClick={() => setOpen(false)}>How it works</a><Link href="/login">Log in</Link><Link href="/signup" className="text-cobalt-light">Get started</Link></nav>
    </div>}
  </>;
}
