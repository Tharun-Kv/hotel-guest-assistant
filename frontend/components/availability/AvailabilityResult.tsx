import type { AvailabilityResult as AvailabilityResultType } from '@/types/availability';
import { formatStay } from '@/lib/utils';
import RoomCard from './RoomCard';

export default function AvailabilityResult({ result }: { result: AvailabilityResultType | null }) {
  if (!result) return null;

  return (
    <section aria-live="polite" className="space-y-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <h2 className="text-lg font-bold text-slate-900">Availability results</h2>
        <p className="mt-1 text-sm text-slate-600">{formatStay(result.check_in, result.check_out)} · {result.adults} guest{result.adults === 1 ? '' : 's'}</p>
        {result.last_synced_at ? <p className="mt-1 text-xs text-slate-500">Live inventory synced {new Date(result.last_synced_at).toLocaleString()}</p> : null}
      </div>
      {result.available ? result.rooms.map((room) => <RoomCard key={room.room_id} room={room} />) : <p className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">No rooms match the requested dates and occupancy.</p>}
    </section>
  );
}
