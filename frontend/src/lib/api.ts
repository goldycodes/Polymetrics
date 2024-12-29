import { Market, MarketCategory, SortBy, SortDirection } from '../types/market';

const API_URL = import.meta.env.VITE_API_URL;

export async function getMarkets(
  category?: MarketCategory,
  sortBy?: SortBy,
  sortDirection: SortDirection = 'desc'
): Promise<Market[]> {
  try {
    const params = new URLSearchParams();
    
    // Only add status if we want active markets
    params.append('status', 'active');
    
    if (category) {
      params.append('category', category.toLowerCase());
    }
    if (sortBy) {
      params.append('sort_by', sortBy.toLowerCase());
      params.append('sort_direction', sortDirection.toLowerCase());
    }
    
    console.log('Building request with params:', Object.fromEntries(params));
    
    const url = `${API_URL}/clob/markets?${params.toString()}`;
    console.log('Making CLOB API request to:', url);
    
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch markets: ${response.status} ${response.statusText}`);
    }
    const rawData = await response.json();
    console.log('Raw CLOB API response:', rawData);
    
    // Transform CLOB response to match Market interface
    const markets = rawData.map((market: any) => ({
      id: market.id?.toString() || '',
      question: market.question || '',
      description: market.description || '',
      volume: (market.volume || '0').toString(),
      open_interest: (market.open_interest || '0').toString(),
      tokens: Array.isArray(market.tokens) ? market.tokens.map((token: any) => ({
        token_id: token.id?.toString() || '',
        name: token.name || '',
        price: (token.price || '0').toString()
      })) : [],
      is_active: market.status?.toLowerCase() === 'active',
      event_status: market.status || 'unknown',
      created_at: market.created_at || '',
      expires_at: market.expires_at || null,
      category: market.category || 'other',
      trader_count: parseInt(market.trader_count || '0', 10)
    }));
    
    console.log('Transformed CLOB markets:', markets);
    return markets;
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
