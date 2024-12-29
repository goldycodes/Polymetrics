export interface MarketToken {
  outcome: string;
  price: number;
}

export interface OpenInterestPoint {
  timestamp: string;
  value: number;
}

export interface Market {
  condition_id: string;
  question: string;
  description: string;
  active: boolean;
  closed: boolean;
  archived: boolean;
  accepting_orders: boolean;
  end_date_iso: string | null;
  game_start_time: string | null;
  market_slug: string;
  tokens: MarketToken[];
  volume: number;
  open_interest: number;
  trader_count: number;
  open_interest_history: OpenInterestPoint[];
}
