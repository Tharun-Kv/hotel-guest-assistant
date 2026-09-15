'use client';

import { useEffect, useState } from 'react';
import {
  Activity,
  ArrowUpRight,
  Bell,
  Bird,
  CalendarDays,
  CircleUserRound,
  Ellipsis,
  Info,
  MessageCircle,
  Pencil,
  Sparkles,
  X,
} from 'lucide-react';

import AvailabilityForm from '@/components/availability/AvailabilityForm';
import AvailabilityResult from '@/components/availability/AvailabilityResult';
import ChatWindow from '@/components/chat/ChatWindow';
import ErrorMessage from '@/components/common/ErrorMessage';
import Sidebar from '@/components/Sidebar';
import { QUICK_ACTIONS } from '@/lib/constants';
import { getHotelInformation } from '@/lib/api';
import { useChat } from '@/hooks/useChat';

function OverviewCard({ icon: Icon, label, value, detail }: { icon: typeof Activity; label: string; value: string; detail: string }) {
  return (
    <article className="rounded-[20px] border border-[#e5e2df] bg-white p-4 shadow-[0_8px_24px_-20px_rgba(15,23,42,0.35)]">
      <div className="flex items-center gap-2 font-sans text-xs font-semibold text-slate-500"><span className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#f1edff] text-violet-700"><Icon size={16} strokeWidth={1.8} aria-hidden="true" /></span>{label}</div>
      <p className="mt-4 text-lg font-bold tracking-tight text-slate-950">{value}</p>
      <p className="mt-1 font-sans text-xs leading-5 text-slate-500">{detail}</p>
    </article>
  );
}

export default function HomePage() {
  const {
    messages,
    loading,
    error,
    availabilityState,
    sendMessage,
    checkRoomAvailability,
    retry,
    clearError,
    resetConversation,
    progressStep,
  } = useChat();
  const [showAvailability, setShowAvailability] = useState(false);
  const [chatOpen, setChatOpen] = useState(true);
  const [chatInfoOpen, setChatInfoOpen] = useState(false);
  const [activeSection, setActiveSection] = useState('overview');
  const [hotelName, setHotelName] = useState<string>();

  useEffect(() => {
    getHotelInformation().then((info) => setHotelName(info.hotel.name)).catch(() => undefined);
  }, []);

  const navigate = (section: string) => {
    setActiveSection(section);
    if (section === 'assistant') {
      setChatOpen(true);
      return;
    }
    if (section === 'guide') {
      setChatOpen(true);
      sendMessage('What hotel amenities and services are available?');
      return;
    }
    if (section === 'rooms') {
      setShowAvailability(true);
      window.setTimeout(() => document.getElementById('room-finder')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 0);
      return;
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <main className="min-h-screen bg-[#f7f6f4] text-slate-950">
      <div className="flex min-h-screen">
        <Sidebar hotelName={hotelName} active={activeSection} onNavigate={navigate} />

        <section className="min-w-0 flex-1">
          <header className="border-b border-[#e5e2df] bg-[#fbfaf9]">
            <div className="flex items-center justify-between gap-4 px-5 py-4 sm:px-8">
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-950 text-violet-300 lg:hidden"><Bird size={17} aria-hidden="true" /></div>
                <div className="min-w-0"><p className="truncate font-sans text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">{hotelName || 'Harbor View Hotel'} / guest journey</p><h1 className="font-display mt-0.5 text-xl font-bold tracking-tight text-slate-950">Stay overview</h1></div>
              </div>
              <div className="flex shrink-0 items-center gap-2 sm:gap-3">
                <button type="button" aria-label="Notifications" className="rounded-xl p-2 text-slate-500 transition hover:bg-white hover:text-slate-950"><Bell size={18} aria-hidden="true" /></button>
                <CircleUserRound size={23} className="text-slate-400" aria-hidden="true" />
              </div>
            </div>
          </header>

          <div className="mx-auto max-w-[1060px] space-y-5 p-5 sm:p-8">
            <section id="overview" className="flex flex-col justify-between gap-5 rounded-[24px] border border-[#e5e2df] bg-white p-6 shadow-[0_12px_32px_-24px_rgba(15,23,42,0.35)] sm:flex-row sm:items-end sm:p-7">
              <div className="max-w-2xl">
                <p className="flex items-center gap-2 font-sans text-xs font-bold uppercase tracking-[0.18em] text-violet-700"><Sparkles size={14} aria-hidden="true" /> Your personal concierge</p>
                <h2 className="font-display mt-3 text-3xl font-bold leading-tight tracking-tight text-slate-950 sm:text-4xl">Everything you need for a smoother stay.</h2>
                <p className="mt-3 max-w-xl font-sans text-sm leading-6 text-slate-500">Ask a question, find the right room, or browse hotel services. Your assistant is ready whenever you are.</p>
              </div>
              <button type="button" onClick={() => { setActiveSection('assistant'); setChatOpen(true); }} className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 font-sans text-sm font-semibold text-white transition hover:bg-violet-700 focus:outline-none focus:ring-4 focus:ring-violet-100"><MessageCircle size={16} aria-hidden="true" /> Open concierge</button>
            </section>

            <div className="grid gap-3 sm:grid-cols-3">
              <OverviewCard icon={CalendarDays} label="Arrival" value="Check in from 3 PM" detail="Front desk support is available around the clock." />
              <OverviewCard icon={Bird} label="Concierge" value="Always on" detail="Ask about rooms, amenities, policies, or the hotel." />
              <OverviewCard icon={Activity} label="Inventory" value="Live updates" detail="Room availability uses the latest operator snapshot." />
            </div>

            <section id="room-finder" className="grid scroll-mt-6 gap-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(280px,.85fr)]">
              <AvailabilityForm onSubmit={(checkIn, checkOut, adults) => { setShowAvailability(true); checkRoomAvailability(checkIn, checkOut, adults); }} loading={loading} />
              <div className="rounded-[22px] border border-[#e5e2df] bg-white p-5 shadow-[0_8px_24px_-20px_rgba(15,23,42,0.35)]">
                <div className="flex items-center justify-between"><div><p className="font-sans text-xs font-bold uppercase tracking-[0.18em] text-violet-700">Concierge shortcuts</p><h2 className="font-display mt-1 text-lg font-bold tracking-tight text-slate-950">What can we help with?</h2></div><Info size={17} className="text-slate-400" aria-hidden="true" /></div>
                <div className="mt-4 space-y-2">
                  {QUICK_ACTIONS.slice(0, 4).map((action) => <button key={action.label} type="button" disabled={loading} onClick={() => { setActiveSection('assistant'); setChatOpen(true); sendMessage(action.message); }} className="group flex w-full items-center justify-between rounded-xl border border-[#ece9e6] bg-[#faf9f8] px-3.5 py-3 text-left font-sans text-sm font-semibold text-slate-700 transition hover:border-violet-200 hover:bg-violet-50 hover:text-violet-900 disabled:cursor-not-allowed disabled:opacity-60"><span className="flex items-center gap-2"><Sparkles size={14} className="text-violet-600" aria-hidden="true" />{action.label}</span><ArrowUpRight size={15} className="text-slate-400 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-violet-700" aria-hidden="true" /></button>)}
                </div>
              </div>
            </section>

            {showAvailability ? <AvailabilityResult result={availabilityState} /> : null}
            {error ? <ErrorMessage message={error} onRetry={retry} onDismiss={clearError} /> : null}
          </div>
        </section>

        {chatOpen ? <button type="button" aria-label="Close chat overlay" className="fixed inset-0 z-40 bg-slate-950/20 backdrop-blur-[2px] lg:hidden" onClick={() => setChatOpen(false)} /> : null}
        <aside aria-label="Hotel assistant chat" className={`fixed inset-x-3 bottom-3 top-3 z-50 transition-all duration-300 lg:sticky lg:inset-auto lg:top-4 lg:mr-4 lg:h-[calc(100vh-2rem)] lg:w-[400px] lg:shrink-0 ${chatOpen ? 'translate-x-0 opacity-100' : 'pointer-events-none translate-x-full opacity-0 lg:hidden'}`}>
          <div className="flex h-full flex-col overflow-hidden rounded-[26px] border border-[#e5e2df] bg-white shadow-[0_20px_60px_-25px_rgba(15,23,42,0.35)]">
            <div className="relative flex items-center justify-between border-b border-[#ece9e6] bg-[#fbf8ff] px-4 py-4">
              <div className="flex items-center gap-2"><span className="flex h-8 w-8 items-center justify-center rounded-xl bg-violet-100 text-violet-700"><Bird size={16} aria-hidden="true" /></span><div><p className="font-sans text-sm font-bold text-slate-950">Little Bird concierge</p><p className="mt-0.5 font-sans text-[11px] text-slate-500">{hotelName || 'Hotel'} guest help</p></div></div>
              <div className="flex items-center gap-1">
                <button type="button" aria-label="Start new conversation" title="Start new conversation" onClick={() => { resetConversation(); setChatInfoOpen(false); }} className="rounded-xl p-2 text-slate-500 transition hover:bg-white hover:text-slate-950"><Pencil size={17} aria-hidden="true" /></button>
                <button type="button" aria-label="Conversation information" title="Conversation information" onClick={() => setChatInfoOpen((current) => !current)} className="rounded-xl p-2 text-slate-500 transition hover:bg-white hover:text-slate-950"><Ellipsis size={18} aria-hidden="true" /></button>
                <button type="button" aria-label="Close chat" title="Close chat" onClick={() => setChatOpen(false)} className="rounded-xl p-2 text-slate-500 transition hover:bg-white hover:text-slate-950"><X size={18} aria-hidden="true" /></button>
              </div>
              {chatInfoOpen ? <div className="absolute right-14 top-14 z-10 w-56 rounded-xl border border-[#e5e2df] bg-white p-3 text-xs shadow-xl"><p className="font-sans font-semibold text-slate-800">Grounded hotel help</p><p className="mt-1 font-sans leading-5 text-slate-500">Answers use approved hotel information. Availability comes from the live inventory feed.</p></div> : null}
            </div>
            <ChatWindow messages={messages} loading={loading} progressStep={progressStep} onSend={sendMessage} className="min-h-0 flex-1 rounded-none border-0 bg-[radial-gradient(circle_at_top,#f8f1ff_0%,#fbfaf9_38%,#f7f6f4_100%)] shadow-none" />
          </div>
        </aside>

        {!chatOpen ? <button type="button" aria-label="Open Little Bird hotel concierge" aria-expanded={false} onClick={() => { setActiveSection('assistant'); setChatOpen(true); }} className="fixed bottom-5 right-5 z-50 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950 text-violet-300 shadow-[0_14px_35px_-10px_rgba(15,23,42,0.65)] transition hover:-translate-y-1 hover:bg-violet-700 focus:outline-none focus:ring-4 focus:ring-violet-200"><Bird size={25} strokeWidth={1.8} aria-hidden="true" /><span className="absolute -right-1 -top-1 h-3.5 w-3.5 rounded-full border-2 border-[#f7f6f4] bg-emerald-400" /></button> : null}
      </div>
    </main>
  );
}
