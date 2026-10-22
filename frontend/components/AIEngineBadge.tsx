"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
export function AIEngineBadge() {
  const [provider,setProvider]=useState<string|null>(null);
  useEffect(()=>{api.get<{connected:boolean;provider:string|null}>("/api/assistant/status").then(x=>setProvider(x.connected?x.provider:null)).catch(()=>setProvider(null));},[]);
  return <span className={`rounded-full px-2 py-1 text-xs font-semibold ${provider?"bg-cobalt-light text-cobalt-dark":"bg-black/5 text-slate"}`}>{provider?`Powered by ${provider[0].toUpperCase()+provider.slice(1)}`:"Offline mode - pattern matching"}</span>;
}
