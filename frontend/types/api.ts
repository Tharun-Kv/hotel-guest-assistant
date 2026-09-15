export interface ApiErrorPayload {
  success?: boolean;
  error?: string;
  detail?: string;
}

export interface HotelInformation {
  hotel: {
    name: string;
    address: string;
    check_in: string;
    check_out: string;
    breakfast: string;
  };
  amenities: Record<string, string>;
  policies: Record<string, string>;
  rooms: Array<Record<string, unknown>>;
}
