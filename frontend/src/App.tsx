import { useState, useEffect } from "react";
import { getMarkets, getMarketById } from "./lib/api";
import { Market } from "./types/market";
import { MarketCard } from "./components/MarketCard";

function App() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [searchId, setSearchId] = useState('');
  const [searchError, setSearchError] = useState('');

  useEffect(() => {
    if (!searchId) {
      fetchMarkets();
    }
  }, [searchId]);

  async function fetchMarkets() {
    try {
      const marketsData = await getMarkets();
      console.log('Fetched markets:', marketsData);
      if (Array.isArray(marketsData)) {
        const activeMarkets = marketsData.filter(market => 
          market.isActive || 
          (market.status === "unknown" && (parseFloat(market.volume || "0") > 0 || parseFloat(market.liquidity || "0") > 0))
        );
        
        if (activeMarkets.length > 0) {
          setMarkets(activeMarkets);
          setError("");
        } else {
          console.warn('No active markets found');
          setError("No active markets found at this time.");
        }
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

  const handleSearch = async () => {
    if (!searchId.trim()) return;
    setLoading(true);
    setSearchError('');
    try {
      const market = await getMarketById(searchId.trim());
      setMarkets([market]);
      setError('');
    } catch (err: any) {
      setSearchError(err.message);
      setMarkets([]);
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setSearchId('');
    setSearchError('');
    fetchMarkets();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col space-y-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-4">Polymarket Dashboard</h1>
            <p className="text-lg text-gray-600">Track live market data and statistics</p>
          </div>
          
          <div className="max-w-3xl mx-auto w-full">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <label htmlFor="market-search" className="block text-sm font-medium text-gray-700 mb-2">
                Search Market by ID
              </label>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <input
                    type="text"
                    id="market-search"
                    value={searchId}
                    onChange={(e) => setSearchId(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Enter market ID..."
                    className="w-full px-6 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                  >
                    {loading ? 'Searching...' : 'Search'}
                  </button>
                  {searchId && (
                    <button
                      onClick={clearSearch}
                      className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors flex-shrink-0"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
              {searchError && (
                <p className="mt-3 text-sm text-red-600 bg-red-50 p-3 rounded-lg">{searchError}</p>
              )}
            </div>
          </div>
        </div>
        
        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center py-32">
            <div className="relative">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-indigo-100 border-t-indigo-600"></div>
            </div>
          </div>
        ) : markets.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Markets Found</h3>
            <p className="text-gray-500">Try changing your filters or check back later.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
            {markets.map((market) => (
              <MarketCard key={market.id} market={market} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
