import { useEffect, useRef } from 'react';

import type { ChatMessage as ChatMessageType, ChatProgressStep } from '@/types/chat';
import { QUICK_ACTIONS } from '@/lib/constants';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import EmptyState from './EmptyState';
import TypingIndicator from './TypingIndicator';

export default function ChatWindow({
  messages,
  loading,
  onSend,
  progressStep,
  className,
}: {
  messages: ChatMessageType[];
  loading: boolean;
  onSend: (value: string) => void;
  progressStep?: ChatProgressStep | null;
  className?: string;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, loading, progressStep]);

  return (
    <section aria-label="Hotel assistant conversation" className={`flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 shadow-sm ${className || 'h-[520px]'}`}>
      <div aria-live="polite" className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 ? <EmptyState /> : messages.map((message) => <ChatMessage key={message.id} role={message.role} content={message.content} responseType={message.responseType} onSend={onSend} sources={message.sources} />)}
        {messages.length === 1 && !loading ? (
          <div className="ml-10 space-y-2">
            <p className="font-sans text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">Popular questions</p>
            <div className="flex flex-wrap gap-2">
              {QUICK_ACTIONS.slice(0, 3).map((action) => (
                <button
                  key={action.label}
                  type="button"
                  onClick={() => onSend(action.message)}
                  className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-left font-sans text-xs font-semibold text-slate-600 transition hover:border-amber-300 hover:bg-amber-50 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-200"
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        ) : null}
        {loading ? <TypingIndicator step={progressStep || 'connecting'} /> : null}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSend={onSend} disabled={loading} />
    </section>
  );
}
