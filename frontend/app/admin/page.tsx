import Link from 'next/link';

import AdminConsole from '@/components/admin/AdminConsole';

export default function AdminPage() {
  return (
    <main className="min-h-screen bg-slate-100 px-4 py-6 sm:px-6 lg:py-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-700">Harbor View operations</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-950">Knowledge and live inventory</h1></div>
          <Link href="/" className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700">Back to assistant</Link>
        </div>
        <AdminConsole />
      </div>
    </main>
  );
}
