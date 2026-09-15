'use client';

import { BookOpen, Building2, CircleHelp, Hotel, LayoutDashboard, MessageCircle, Settings2 } from 'lucide-react';

type SidebarProps = {
  hotelName?: string;
  active: string;
  onNavigate: (section: string) => void;
};

const items = [
  { id: 'overview', label: 'Stay overview', icon: LayoutDashboard },
  { id: 'assistant', label: 'Concierge', icon: MessageCircle },
  { id: 'rooms', label: 'Room finder', icon: Building2 },
  { id: 'guide', label: 'Hotel guide', icon: BookOpen },
];

export default function Sidebar({ hotelName, active, onNavigate }: SidebarProps) {
  return (
    <aside className="hidden w-[236px] shrink-0 flex-col border-r border-[#e5e2df] bg-[#efedeb] px-3 py-4 lg:flex">
      <div className="flex items-center justify-between px-2">
        <div className="flex min-w-0 items-center gap-2.5">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-950 text-violet-300"><Hotel size={17} strokeWidth={1.8} aria-hidden="true" /></div>
          <div className="min-w-0">
            <p className="truncate font-sans text-xs font-bold text-slate-900">{hotelName || 'Harbor View Hotel'}</p>
            <p className="font-sans text-[10px] text-slate-500">Guest experience</p>
          </div>
        </div>
        <button type="button" aria-label="Open hotel account menu" className="rounded-lg p-1.5 text-slate-500 transition hover:bg-white hover:text-slate-900"><Settings2 size={15} aria-hidden="true" /></button>
      </div>

      <nav aria-label="Guest assistant navigation" className="mt-8 space-y-1">
        <p className="px-3 pb-2 font-sans text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Your stay</p>
        {items.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => onNavigate(id)}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left font-sans text-sm font-semibold transition ${active === id ? 'bg-violet-100 text-violet-800 shadow-sm' : 'text-slate-600 hover:bg-white hover:text-slate-950'}`}
          >
            <Icon size={17} strokeWidth={1.8} aria-hidden="true" />
            {label}
          </button>
        ))}
      </nav>

      <div className="mt-8 border-t border-[#ddd9d5] pt-6">
        <p className="px-3 pb-2 font-sans text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">Hotel tools</p>
        <a href="/admin" className="flex items-center gap-3 rounded-xl px-3 py-2.5 font-sans text-sm font-semibold text-slate-600 transition hover:bg-white hover:text-slate-950"><Settings2 size={17} strokeWidth={1.8} aria-hidden="true" /> Hotel operations</a>
      </div>

      <div className="mt-auto rounded-2xl border border-white/80 bg-white/70 p-3">
        <div className="flex items-start gap-2.5">
          <CircleHelp size={17} className="mt-0.5 shrink-0 text-violet-600" aria-hidden="true" />
          <div><p className="font-sans text-xs font-bold text-slate-800">Need a hand?</p><p className="mt-1 font-sans text-[11px] leading-4 text-slate-500">Ask the concierge about anything at the hotel.</p></div>
        </div>
      </div>
    </aside>
  );
}
