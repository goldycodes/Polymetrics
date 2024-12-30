// Market interface for Gamma API
export interface Market {
  id: string;
  question: string;
  description?: string;
  volume: string;
  openInterest: string;
  categories: string[];
  createdTimestamp: string;
  isActive?: boolean;
}
