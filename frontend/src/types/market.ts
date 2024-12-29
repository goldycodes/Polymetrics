// Simplified Market interface for MVP
export interface Market {
  id: string;
  question: string;
  volume: string;
  open_interest: string;
  trader_count: number;
  event_status: string;
  is_active: boolean;
}
