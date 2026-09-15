import { FormEvent, KeyboardEvent, useState } from 'react';
import { ArrowUp } from 'lucide-react';

import { MAX_MESSAGE_LENGTH } from '@/lib/constants';

export default function ChatInput({ onSend, disabled }: { onSend: (value: string) => void; disabled: boolean }) {
  const [value, setValue] = useState('');

  const submit = () => {
    const message = value.trim();
    if (!message || disabled) return;
    onSend(message);
    setValue('');
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    submit();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-white p-3">
      <label className="sr-only" htmlFor="guest-message">Ask the assistant</label>
      <div className="flex items-center gap-2 rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2 transition focus-within:border-amber-400 focus-within:bg-white focus-within:ring-2 focus-within:ring-amber-100">
        <input id="guest-message" value={value} onChange={(event) => setValue(event.target.value)} onKeyDown={handleKeyDown} disabled={disabled} maxLength={MAX_MESSAGE_LENGTH} placeholder="Ask your concierge anything..." className="min-w-0 flex-1 bg-transparent py-1 font-sans text-sm outline-none placeholder:text-slate-400 disabled:opacity-60" />
        <button type="submit" aria-label="Send message" disabled={disabled || !value.trim()} className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-amber-300 disabled:cursor-not-allowed disabled:bg-slate-300"><ArrowUp size={18} strokeWidth={2.5} aria-hidden="true" /></button>
      </div>
      <p className="mt-2 text-center font-sans text-[10px] text-slate-400">AI responses are grounded in verified hotel information</p>
    </form>
  );
}
