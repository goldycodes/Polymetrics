import { Market } from '../types/market';

const API_URL = import.meta.env.VITE_API_URL;
const API_USER = import.meta.env.VITE_API_USER;
const API_KEY = import.meta.env.VITE_API_KEY;

const headers = {
  'Authorization': 'Basic ' + btoa(`${API_USER}:${API_KEY}`)
};

export async function getMarkets(): Promise<Market[]> {
  try {
    console.log('Fetching active markets from Gamma API');
    const response = await fetch(`${API_URL}/gamma/markets?current_only=true`, {
      headers
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch markets: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log('Gamma API response:', data);
    return data || [];
  } catch (error) {
    console.error('Error fetching markets:', error);
    return [];
  }
}

export async function getSportsMarkets(): Promise<Market[]> {
  try {
    console.log('Fetching sports markets from Gamma API');
    const response = await fetch(`${API_URL}/gamma/markets/sports`, {
      headers
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch sports markets: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    console.log('Sports markets response:', data);
    return data || [];
  } catch (error) {
    console.error('Error fetching sports markets:', error);
    return [];
  }
}
