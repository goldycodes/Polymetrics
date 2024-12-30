import { useState, useEffect } from "react";
import { getMarkets, getSportsMarkets, getMarketById } from "./lib/api";
import { Market } from "./types/market";
import { MarketCard } from "./components/MarketCard";

function App() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showSportsOnly, setShowSportsOnly] = useState(false);
  const [searchId, setSearchId] = useState('');
  const [searchError, setSearchError] = useState('');

  // Reset search when toggling between all/sports markets
  useEffect(() => {
    if (searchId) {
      setSearchId('');
      setSearchError('');
    }
  }, [showSportsOnly]);

  useEffect(() => {
    if (!searchId) {
      fetchMarkets();
    }
  }, [searchId]);

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

  async function fetchSportsMarkets() {
    try {
      const marketsData = await getSportsMarkets();
      console.log('Fetched sports markets:', marketsData);
      if (Array.isArray(marketsData) && marketsData.length > 0) {
        setMarkets(marketsData);
        setError("");
      } else if (Array.isArray(marketsData) && marketsData.length === 0) {
        console.warn('No sports markets returned from API');
        setError("No active sports markets found at this time.");
      } else {
        console.error('Unexpected data format:', marketsData);
        setError("Unable to load sports markets. Please try again later.");
      }
    } catch (err) {
      console.error('Error fetching sports markets:', err);
      setError("Failed to fetch sports markets. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  const toggleMarketView = () => {
    setLoading(true);
    setShowSportsOnly(!showSportsOnly);
    if (!showSportsOnly) {
      fetchSportsMarkets();
    } else {
      fetchMarkets();
    }
  };

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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col space-y-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-extrabold text-gray-900">Polymarket Dashboard</h1>
            <button
              onClick={toggleMarketView}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
            >
              {showSportsOnly ? 'Show All Markets' : 'Show Sports Markets'}
            </button>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex-1 max-w-md">
              <label htmlFor="market-search" className="block text-sm font-medium text-gray-700 mb-1">
                Search Market by ID
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  id="market-search"
                  value={searchId}
                  onChange={(e) => setSearchId(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Enter market ID..."
                  className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                <button
                  onClick={handleSearch}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Search
                </button>
              </div>
              {searchError && (
                <p className="mt-1 text-sm text-red-600">{searchError}</p>
              )}
            </div>
            {searchId && (
              <button
                onClick={clearSearch}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Clear Search
              </button>
            )}
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
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : markets.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Markets Found</h3>
            <p className="text-gray-500">Try changing your filters or check back later.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
