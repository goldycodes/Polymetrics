export interface MarketToken {
  token_id: string;
  name: string;
  price: string;
}

export interface Market {
  id: string;
  question: string;
  description: string | null;
  volume: string | null;
  open_interest?: string | null;
  tokens: MarketToken[];
  is_active: boolean;
  event_status: string;
  created_at: string;
  expires_at: string | null;
}
