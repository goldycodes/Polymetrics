export interface MarketToken {
  token_id: string;
  name: string;
  price: string;
}

export interface OpenInterestPoint {
  timestamp: number;
  value: number;
}

export type MarketCategory = 'sports' | 'crypto' | 'politics' | 'entertainment' | 'other';
export type SortDirection = 'asc' | 'desc';
export type SortBy = 'volume' | 'created_at';

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
  category?: MarketCategory;
}
