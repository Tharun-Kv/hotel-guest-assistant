import { FormEvent, useState } from 'react';

import { todayIsoDate } from '@/lib/utils';

export default function AvailabilityForm({
  onSubmit,
  loading,
}: {
  onSubmit: (checkIn: string, checkOut: string, adults: number) => void;
  loading: boolean;
}) {
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [adults, setAdults] = useState(2);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!checkIn || !checkOut) {
      setValidationError('Select both check-in and check-out dates.');
      return;
    }
    if (checkOut <= checkIn) {
      setValidationError('Check-out must be after check-in.');
      return;
    }
    setValidationError(null);
    onSubmit(checkIn, checkOut, adults);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700">Planning a stay</p>
        <h2 className="mt-1 text-lg font-bold text-slate-900">Check availability</h2>
      </div>
      <div className="space-y-3">
        <label className="block text-sm font-medium text-slate-700">
          Check-in
          <input type="date" min={todayIsoDate()} required value={checkIn} onChange={(event) => setCheckIn(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100" />
        </label>
        <label className="block text-sm font-medium text-slate-700">
          Check-out
          <input type="date" min={checkIn || todayIsoDate()} required value={checkOut} onChange={(event) => setCheckOut(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100" />
        </label>
        <label className="block text-sm font-medium text-slate-700">
          Guests
          <input type="number" min={1} max={10} required value={adults} onChange={(event) => setAdults(Math.max(1, Number(event.target.value) || 1))} className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-100" />
        </label>
      </div>
      {validationError ? <p role="alert" className="text-sm text-red-700">{validationError}</p> : null}
      <button type="submit" disabled={loading} className="w-full rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-300 disabled:cursor-not-allowed disabled:bg-slate-300">
        {loading ? 'Checking…' : 'Check rooms'}
      </button>
    </form>
  );
}
