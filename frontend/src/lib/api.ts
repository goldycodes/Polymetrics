import { Market } from '../types/market';

const API_BASE_URL = 'http://localhost:8000';

// Helper function to log detailed error information
const logDetailedError = (error: any, context: string) => {
  console.error(`${context} Details:`, {
    message: error.message,
    stack: error.stack,
    response: error.response,
    type: error.type
  });
};

export async function getMarkets(): Promise<Market[]> {
  try {
    console.log('Fetching active markets from Gamma API');
    const response = await fetch(`${API_BASE_URL}/markets/gamma`);

    if (!response.ok) {
      throw new Error(`Failed to fetch markets: ${response.status}`);
    }

    const data = await response.json();
    console.log('Gamma API response:', data);
    return data;
  } catch (error: any) {
    logDetailedError(error, 'Error fetching markets');
    return [];
  }
}

export async function getMarketById(marketId: string): Promise<Market> {
  try {
    console.log(`Fetching market ${marketId} from Gamma API`);
    const response = await fetch(`${API_BASE_URL}/markets/gamma/${marketId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Market not found');
      }
      throw new Error(`Failed to fetch market: ${response.status}`);
    }

    const data = await response.json();
    console.log('Market response:', data);
    return data;
  } catch (error: any) {
    console.error('Error fetching market:', error);
    throw error;
  }
}

export async function getSportsMarkets(): Promise<Market[]> {
  try {
    console.log('Fetching sports markets from Gamma API');
    const response = await fetch(`${API_BASE_URL}/markets/gamma/sports`);

    if (!response.ok) {
      throw new Error(`Failed to fetch sports markets: ${response.status}`);
    }

    const data = await response.json();
    console.log('Sports markets response:', data);
    return data;
  } catch (error: any) {
    logDetailedError(error, 'Error fetching sports markets');
    return [];
  }
}
