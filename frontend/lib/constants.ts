export const API_TIMEOUT_MS = 12_000;
export const MAX_MESSAGE_LENGTH = 1_000;

export const QUICK_ACTIONS = [
  { label: 'Check-in time', message: 'What time is check-in?' },
  { label: 'Breakfast', message: 'Is breakfast included?' },
  { label: 'Swimming pool', message: 'Does the hotel have a swimming pool?' },
  { label: 'Room for 3 guests', message: 'Which room is good for 3 people?' },
] as const;
