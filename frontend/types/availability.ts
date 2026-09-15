export interface AvailabilityResultRoom {
  room_id: string;
  name: string;
  capacity: number;
  bed_configuration: string;
  description: string;
  amenities: string[];
  price_per_night: number;
}

export interface AvailabilityResult {
  hotel_id?: string;
  available: boolean;
  rooms: AvailabilityResultRoom[];
  check_in: string;
  check_out: string;
  adults: number;
  last_synced_at?: string | null;
}
