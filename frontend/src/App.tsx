import { useState, useEffect } from "react";
import { getMarkets } from "./lib/api";
import { Market } from "./types/market";
import { MarketCard } from "./components/MarketCard";

function App() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarkets();
  }, []);

  async function fetchMarkets() {
    try {
      const marketsData = await getMarkets();
      console.log('Fetched markets:', marketsData);
      if (Array.isArray(marketsData) && marketsData.length > 0) {
        setMarkets(marketsData);
        setError("");
      } else if (Array.isArray(marketsData) && marketsData.length === 0) {
        console.warn('No markets returned from API');
        setError("No active markets found. This could be due to rate limiting. Please try again in a few minutes.");
      } else {
        console.error('Unexpected data format:', marketsData);
        setError("Unable to load markets. Please try again later.");
      }
    } catch (err) {
      console.error('Error fetching markets:', err);
      setError("Failed to fetch markets. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="p-8">Loading markets...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Polymarket Dashboard</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="container mx-auto px-4">
        <div 
          data-testid="market-grid" 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {markets.map((market) => (
            <MarketCard key={market.id} market={market} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
