export function formatStay(checkIn: string, checkOut: string): string {
  const format = (value: string) =>
    new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(
      new Date(`${value}T00:00:00`),
    );
  return `${format(checkIn)} – ${format(checkOut)}`;
}

export function todayIsoDate(): string {
  const now = new Date();
  const offset = now.getTimezoneOffset() * 60_000;
  return new Date(now.getTime() - offset).toISOString().slice(0, 10);
}
