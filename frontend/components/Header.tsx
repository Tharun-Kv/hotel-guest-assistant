import { Bell, CircleUserRound, Sparkles } from 'lucide-react';

export default function Header({ hotelName }: { hotelName?: string }) {
  return (
    <header className="border-b border-slate-200/80 bg-white/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-slate-900 text-amber-300 shadow-sm">
            <Sparkles size={21} strokeWidth={1.8} aria-hidden="true" />
          </div>
          <div>
            <p className="font-sans text-[10px] font-bold uppercase tracking-[0.22em] text-amber-700">{hotelName || 'Hotel concierge'}</p>
            <h1 className="font-display text-xl font-bold tracking-tight text-slate-950">Guest Assistant</h1>
          </div>
        </div>
        <div className="hidden items-center gap-3 sm:flex">
          <a href="/admin" className="text-xs font-semibold text-slate-600 transition hover:text-amber-700">Hotel operations</a>
          <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 font-sans text-xs font-semibold text-emerald-800">
            <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden="true" /> Online now
          </div>
          <button type="button" aria-label="Notifications" className="rounded-full p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900">
            <Bell size={18} aria-hidden="true" />
          </button>
          <CircleUserRound size={23} className="text-slate-400" aria-hidden="true" />
        </div>
      </div>
    </header>
  );
}
