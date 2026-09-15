'use client';

import { useState } from 'react';

import {
  getLiveInventory,
  ingestKnowledgeSource,
  listKnowledgeDocuments,
  searchKnowledge,
  updateLiveInventory,
  type InventorySnapshot,
  type KnowledgeDocument,
  type KnowledgeSearchResult,
} from '@/lib/api';

const EMPTY_INVENTORY: InventorySnapshot = {
  hotel_id: 'default',
  last_synced_at: null,
  rooms: [],
  bookings: [],
};

export default function AdminConsole() {
  const [token, setToken] = useState('');
  const [hotelId, setHotelId] = useState('default');
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [manualContent, setManualContent] = useState('');
  const [inventoryJson, setInventoryJson] = useState(JSON.stringify(EMPTY_INVENTORY, null, 2));
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<KnowledgeSearchResult[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async (operation: () => Promise<void>) => {
    setError(null);
    setStatus(null);
    try {
      await operation();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'The operation could not be completed.');
    }
  };

  const loadDocuments = () => run(async () => {
    setDocuments(await listKnowledgeDocuments(token, hotelId));
    setStatus('Knowledge documents refreshed.');
  });

  const ingest = () => run(async () => {
    if (url.trim()) {
      await ingestKnowledgeSource({ url: url.trim(), title: title.trim() || undefined, hotel_id: hotelId }, token);
    } else {
      await ingestKnowledgeSource({ content: manualContent, title: title.trim(), hotel_id: hotelId }, token);
    }
    setUrl('');
    setManualContent('');
    await loadDocuments();
    setStatus('Source ingested and indexed for grounded answers.');
  });

  const loadInventory = () => run(async () => {
    const snapshot = await getLiveInventory(token, hotelId);
    setInventoryJson(JSON.stringify(snapshot, null, 2));
    setStatus('Live inventory loaded.');
  });

  const saveInventory = () => run(async () => {
    const snapshot = JSON.parse(inventoryJson) as InventorySnapshot;
    const saved = await updateLiveInventory(snapshot, token);
    setInventoryJson(JSON.stringify(saved, null, 2));
    setStatus('Live inventory updated. New availability checks use this snapshot immediately.');
  });

  const runSearch = () => run(async () => {
    const response = await searchKnowledge(searchQuery, hotelId);
    setSearchResults(response.results);
  });

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-950">
        <p className="font-semibold">Hotel operations workspace</p>
        <p className="mt-1 leading-6">Ingest public hotel pages or approved text into the retrieval index, then update the live room snapshot used by availability. Configure <code>ADMIN_API_TOKEN</code> outside local development.</p>
        <label className="mt-3 block font-medium">Admin token (optional in local development)
          <input type="password" value={token} onChange={(event) => setToken(event.target.value)} className="mt-1 block w-full rounded-lg border border-amber-300 bg-white px-3 py-2 text-slate-900 outline-none focus:ring-2 focus:ring-amber-300" placeholder="X-Admin-Token" />
        </label>
      </section>

      {error ? <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</div> : null}
      {status ? <div role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">{status}</div> : null}

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div><p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700">RAG knowledge</p><h2 className="mt-1 text-xl font-bold text-slate-950">Scrape and index a hotel source</h2></div>
          <label className="text-sm font-medium text-slate-700">Hotel ID<input value={hotelId} onChange={(event) => setHotelId(event.target.value)} className="mt-1 block rounded-lg border border-slate-300 px-3 py-2" /></label>
        </div>
        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-slate-700">Public page URL<input value={url} onChange={(event) => setUrl(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="https://hotel.example.com/amenities" /></label>
            <label className="mt-3 block text-sm font-medium text-slate-700">Document title<input value={title} onChange={(event) => setTitle(event.target.value)} className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="Amenities and policies" /></label>
          </div>
          <label className="block text-sm font-medium text-slate-700">Or paste approved text<textarea value={manualContent} onChange={(event) => setManualContent(event.target.value)} className="mt-1 h-28 w-full rounded-lg border border-slate-300 px-3 py-2" placeholder="Paste hotel policy content here…" /></label>
        </div>
        <div className="mt-4 flex flex-wrap gap-2"><button type="button" onClick={ingest} disabled={!url.trim() && !manualContent.trim()} className="rounded-lg bg-slate-950 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300">Ingest source</button><button type="button" onClick={loadDocuments} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">List indexed sources</button></div>
        {documents.length ? <ul className="mt-4 space-y-2 text-sm text-slate-600">{documents.map((document) => <li key={document.document_id} className="rounded-lg bg-slate-50 px-3 py-2"><span className="font-semibold text-slate-900">{document.title}</span> · {document.chunk_count} chunks · {document.source_url}</li>)}</ul> : null}
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700">Live inventory</p><h2 className="mt-1 text-xl font-bold text-slate-950">Update rooms and bookings</h2>
        <p className="mt-1 text-sm leading-6 text-slate-600">Edit the JSON snapshot below. Room status, prices, and booking intervals are applied atomically to the availability engine.</p>
        <textarea value={inventoryJson} onChange={(event) => setInventoryJson(event.target.value)} className="mt-4 h-80 w-full rounded-xl border border-slate-300 bg-slate-950 p-4 font-mono text-xs text-emerald-100 outline-none focus:ring-2 focus:ring-amber-300" spellCheck={false} />
        <div className="mt-3 flex flex-wrap gap-2"><button type="button" onClick={loadInventory} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700">Reload snapshot</button><button type="button" onClick={saveInventory} className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-700">Save live inventory</button></div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700">Retrieval check</p><h2 className="mt-1 text-xl font-bold text-slate-950">Search indexed context</h2>
        <div className="mt-3 flex gap-2"><input value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2" placeholder="Search an indexed hotel policy…" /><button type="button" onClick={runSearch} disabled={searchQuery.trim().length < 2} className="rounded-lg bg-slate-950 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300">Search</button></div>
        {searchResults.length ? <div className="mt-4 space-y-3">{searchResults.map((result) => <article key={result.chunk_id} className="rounded-lg bg-slate-50 p-3 text-sm"><p className="font-semibold text-slate-900">{result.title} · relevance {result.score}</p><p className="mt-1 text-slate-600">{result.text}</p></article>)}</div> : null}
      </section>
    </div>
  );
}
