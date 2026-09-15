export default function ErrorMessage({ message, onRetry, onDismiss }: { message: string; onRetry?: () => void; onDismiss: () => void }) {
  return (
    <div role="alert" className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
      <span>{message}</span>
      <div className="flex gap-2">
        {onRetry ? <button type="button" onClick={onRetry} className="font-semibold underline underline-offset-2">Retry</button> : null}
        <button type="button" onClick={onDismiss} className="font-semibold underline underline-offset-2">Dismiss</button>
      </div>
    </div>
  );
}
