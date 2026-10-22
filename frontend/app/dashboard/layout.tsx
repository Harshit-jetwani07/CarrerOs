import { Sidebar } from "@/components/Sidebar";
import { AssistantPanel } from "@/components/AssistantPanel";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-paper">
      <Sidebar />
      <main className="flex-1 px-10 py-10 max-w-5xl">{children}</main>
      <AssistantPanel />
    </div>
  );
}
