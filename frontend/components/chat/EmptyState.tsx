import { Bird, MessageCircleMore } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center p-8 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-700 shadow-lg shadow-violet-900/10"><Bird size={25} strokeWidth={1.7} aria-hidden="true" /></div>
      <h3 className="mt-4 text-lg font-bold text-slate-900">Little Bird is ready to help</h3>
      <p className="mt-2 max-w-sm font-sans text-sm leading-6 text-slate-500">Ask about check-in, breakfast, the pool, or room availability and I’ll point you in the right direction.</p>
      <div className="mt-5 flex items-center gap-2 font-sans text-xs font-semibold text-slate-400"><MessageCircleMore size={15} /> Your conversation starts here</div>
    </div>
  );
}
