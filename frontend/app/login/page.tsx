"use client";

import Link from "next/link";
import { AlertCircle, Eye, EyeOff, LoaderCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthShell } from "@/components/AuthShell";
import { login } from "@/lib/api";
import { saveToken } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter(); const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [showPassword, setShowPassword] = useState(false); const [submitting, setSubmitting] = useState(false); const [error, setError] = useState(""); const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); const nextErrors: { email?: string; password?: string } = {};
    if (!/^\S+@\S+\.\S+$/.test(email)) nextErrors.email = "Enter a valid email address."; if (!password) nextErrors.password = "Enter your password.";
    setErrors(nextErrors); setError(""); if (Object.keys(nextErrors).length) return;
    setSubmitting(true); try { const { access_token } = await login(email, password); saveToken(access_token); router.push("/dashboard"); } catch (caught) { setError(caught instanceof Error ? caught.message : "We could not log you in. Please try again."); } finally { setSubmitting(false); }
  }
  return <AuthShell><h1 className="mt-10 font-display text-3xl font-semibold tracking-tight">Welcome back</h1><p className="mt-2 text-slate">Log in to see what should come next.</p>{error && <div className="mt-6 flex gap-3 rounded-md border border-rust/20 bg-rust-light p-3 text-sm text-rust" role="alert"><AlertCircle className="mt-0.5 shrink-0" size={17} />{error}</div>}<form className="mt-8 space-y-5" onSubmit={submit} noValidate><div><label htmlFor="email" className="text-sm font-medium">Email</label><input id="email" type="email" value={email} disabled={submitting} onChange={(event) => setEmail(event.target.value)} className="auth-input mt-1.5" autoComplete="email" />{errors.email && <p className="field-error">{errors.email}</p>}</div><div><div className="flex items-center justify-between"><label htmlFor="password" className="text-sm font-medium">Password</label><span className="text-xs text-slate" title="Password reset is not enabled in this local demo">Password reset unavailable</span></div><div className="relative mt-1.5"><input id="password" type={showPassword ? "text" : "password"} value={password} disabled={submitting} onChange={(event) => setPassword(event.target.value)} className="auth-input pr-11" autoComplete="current-password" /><button type="button" onClick={() => setShowPassword((value) => !value)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate hover:text-ink" aria-label={showPassword ? "Hide password" : "Show password"}>{showPassword ? <EyeOff size={18} /> : <Eye size={18} />}</button></div>{errors.password && <p className="field-error">{errors.password}</p>}</div><button type="submit" disabled={submitting} className="flex h-11 w-full items-center justify-center gap-2 rounded-md bg-ink text-sm font-medium text-white transition hover:bg-cobalt disabled:cursor-not-allowed disabled:opacity-60">{submitting && <LoaderCircle size={17} className="animate-spin" />}{submitting ? "Logging in..." : "Log in"}</button></form><p className="mt-7 text-sm text-slate">New here? <Link href="/signup" className="font-medium text-cobalt hover:text-cobalt-dark">Create an account</Link></p></AuthShell>;
}
