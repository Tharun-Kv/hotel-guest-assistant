import { Bird, Check, Circle, Timer } from 'lucide-react';

import type { ChatProgressStep } from '@/types/chat';

const STEPS: Array<{ id: ChatProgressStep; label: string }> = [
  { id: 'connecting', label: 'Connecting to the concierge' },
  { id: 'checking', label: 'Checking hotel information' },
  { id: 'preparing', label: 'Preparing your answer' },
];

export default function TypingIndicator({ step = 'connecting' }: { step?: ChatProgressStep }) {
  const activeIndex = STEPS.findIndex((item) => item.id === step);

  return (
    <div className="flex items-end gap-2.5">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-violet-100 text-violet-700"><Bird size={15} aria-hidden="true" /></div>
      <div role="status" aria-live="polite" className="min-w-[230px] rounded-2xl rounded-bl-md border border-violet-100 bg-white px-4 py-3 font-sans text-sm text-slate-600 shadow-sm">
        <div className="flex items-center gap-2 font-semibold text-slate-800"><Timer size={15} className="concierge-thinking-timer text-violet-600" aria-hidden="true" /> Working on that</div>
        <ol className="mt-2 space-y-1.5">
          {STEPS.map((item, index) => (
            <li key={item.id} className={`flex items-center gap-2 text-xs ${index <= activeIndex ? 'text-slate-700' : 'text-slate-400'}`}>
              <span className="flex h-4 w-4 items-center justify-center">
                {index < activeIndex ? <Check size={13} className="text-emerald-600" aria-hidden="true" /> : index === activeIndex ? <Timer size={13} className="concierge-step-timer text-violet-600" aria-hidden="true" /> : <Circle size={10} className="text-slate-300" aria-hidden="true" />}
              </span>
              {item.label}
            </li>
          ))}
        </ol>
        <div className="mt-2 flex gap-1.5 pl-6">
          <span className="concierge-thinking-dot h-1.5 w-1.5 rounded-full bg-violet-400 [animation-delay:-0.4s]" />
          <span className="concierge-thinking-dot h-1.5 w-1.5 rounded-full bg-violet-400 [animation-delay:-0.2s]" />
          <span className="concierge-thinking-dot h-1.5 w-1.5 rounded-full bg-violet-400" />
        </div>
      </div>
    </div>
  );
}
