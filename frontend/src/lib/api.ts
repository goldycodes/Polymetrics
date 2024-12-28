/// <reference types="vite/client" />
export const API_URL = import.meta.env.VITE_API_URL;

export async function getMarkets() {
  try {
    const response = await fetch(`${API_URL}/api/markets`);
    if (!response.ok) {
      throw new Error('Failed to fetch markets');
    }
    const data = await response.json();
    
    // Transform the data to match our Market interface
    return data.map((market: any) => ({
      id: market.id,
      question: market.condition?.question || '',
      description: market.condition?.question || '',
      volume: parseFloat(market.collateralVolume || '0'),
      open_interest: 0, // Will be fetched separately
      trader_count: 0,  // Will be fetched separately
      tokens: (market.condition?.outcomes || []).map((outcome: string, index: number) => ({
        outcome: outcome,
        price: parseFloat(market.outcomeTokenPrices?.[index] || '0')
      })),
      creationTimestamp: market.creationTimestamp,
      lastActiveDay: market.lastActiveTimestamp,
      outcomeTokenPrices: market.outcomeTokenPrices || []
    }));
  } catch (error) {
    console.error('Error fetching markets:', error);
    throw error;
  }
}

export async function getMarketOrders(marketId: string) {
  const response = await fetch(`${API_URL}/api/markets/${marketId}/orders`);
  if (!response.ok) {
    throw new Error('Failed to fetch market orders');
  }
  return response.json();
}
