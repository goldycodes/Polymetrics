export interface Token {
  outcome: string;
  price: number;
}

export interface Market {
  id: string;
  question: string;
  description: string;
  endDate: string;
  volume: number;
  open_interest: number;
  trader_count: number;
  tokens: Token[];
  creationTimestamp: string;
  lastActiveDay: string;
  scaledCollateralVolume: string;
  outcomeTokenPrices: string[];
  tradesQuantity: string;
  condition: {
    id: string;
    question: string;
    resolutionTimestamp: string;
  } | null;
}

export interface OrderBook {
  bids: Array<{
    price: number;
    size: number;
  }>;
  asks: Array<{
    price: number;
    size: number;
  }>;
}

export interface MarketStats {
  volume: number;
  open_interest: number;
  trader_count: number;
}
