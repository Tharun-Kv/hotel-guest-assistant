import type { AvailabilityResultRoom } from '@/types/availability';

export default function RoomCard({ room }: { room: AvailabilityResultRoom }) {
  return (
    <article className="rounded-xl border border-slate-200 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-slate-900">{room.name}</h3>
          <p className="mt-1 text-sm text-slate-600">{room.description}</p>
        </div>
        <span className="shrink-0 rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-800">Available</span>
      </div>
      <dl className="mt-3 space-y-1 text-sm text-slate-600">
        <div className="flex justify-between gap-3"><dt>Capacity</dt><dd>{room.capacity} guests</dd></div>
        <div className="flex justify-between gap-3"><dt>Beds</dt><dd className="text-right">{room.bed_configuration}</dd></div>
        <div className="flex justify-between gap-3"><dt>From</dt><dd>${room.price_per_night}/night</dd></div>
      </dl>
    </article>
  );
}
