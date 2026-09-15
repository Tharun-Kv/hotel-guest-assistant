import { Bird, UserRound } from 'lucide-react';
import type { ChatResponseType } from '@/types/chat';

type ChatMessageProps = {
  role: 'user' | 'assistant';
  content: string;
  responseType?: ChatResponseType;
  onSend?: (value: string) => void;
  sources?: Array<{ title: string; url: string }>;
};

function getFollowUpOptions(content: string): string[] {
  const text = content.toLowerCase();
  if (text.includes('how many guests') || text.includes('how many people') || text.includes('guest count')) {
    return ['I am staying with 2 adults', 'I am staying with 3 adults'];
  }
  if (text.includes('check-in') || text.includes('check in') || text.includes('check-out') || text.includes('check out')) {
    return ['My dates are 2026-10-10 to 2026-10-12', 'What dates are available?'];
  }
  return ['What rooms are available?', 'Can you recommend a room?'];
}

export default function ChatMessage({ role, content, responseType, onSend, sources = [] }: ChatMessageProps) {
  const isUser = role === 'user';
  const followUpOptions = !isUser && responseType === 'clarification' ? getFollowUpOptions(content) : [];

  return (
    <div className={`flex items-end gap-2.5 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser ? <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-violet-100 text-violet-700"><Bird size={15} aria-hidden="true" /></div> : null}
      <div className={`max-w-[85%] rounded-2xl px-4 py-3 font-sans text-sm leading-6 shadow-sm ${isUser ? 'rounded-br-md bg-slate-900 text-white' : 'rounded-bl-md border border-slate-200/80 bg-white text-slate-800'}`}>
        <p>{content}</p>
        {!isUser && sources.length ? (
          <div className="mt-3 border-t border-slate-200 pt-2 text-xs text-slate-500">
            <p className="font-semibold text-slate-600">Sources</p>
            <ul className="mt-1 space-y-1">
              {sources.map((source) => (
                <li key={`${source.title}-${source.url}`}>
                  {source.url.startsWith('http') ? <a href={source.url} target="_blank" rel="noreferrer" className="underline underline-offset-2 hover:text-blue-700">{source.title}</a> : source.title}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        {followUpOptions.length ? (
          <div className="mt-3 border-t border-slate-200 pt-3">
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.14em] text-slate-400">Next question</p>
            <div className="flex flex-wrap gap-2">
              {followUpOptions.map((option) => (
                <button key={option} type="button" onClick={() => onSend?.(option)} className="rounded-full border border-amber-200 bg-amber-50 px-3 py-1.5 text-left text-xs font-semibold text-amber-900 transition hover:border-amber-400 hover:bg-amber-100 focus:outline-none focus:ring-2 focus:ring-amber-300">{option}</button>
              ))}
            </div>
          </div>
        ) : null}
      </div>
      {isUser ? <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-800"><UserRound size={15} aria-hidden="true" /></div> : null}
    </div>
  );
}
