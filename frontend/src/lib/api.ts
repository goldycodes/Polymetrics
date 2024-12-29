import { Market } from '../types/market';

const API_URL = import.meta.env.VITE_API_URL;

export async function getMarkets(): Promise<Market[]> {
  try {
    console.log('Making API request to:', `${API_URL}/api/markets`);
    const response = await fetch(`${API_URL}/api/markets`);
    if (!response.ok) {
      throw new Error(`Failed to fetch markets: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log('API response:', data);
    return data;
  } catch (error) {
    console.error('Error fetching markets:', error);
    return [];
  }
}

export async function fetchGammaMarkets(currentOnly: boolean = true): Promise<Market[]> {
  try {
    console.log('Making Gamma API request to:', `${API_URL}/gamma/markets?current_only=${currentOnly}`);
    const response = await fetch(`${API_URL}/gamma/markets?current_only=${currentOnly}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch gamma markets: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log('Gamma API response:', data);
    return data;
  } catch (error) {
    console.error('Error fetching gamma markets:', error);
    return [];
  }
}
