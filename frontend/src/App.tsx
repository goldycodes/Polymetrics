import { useState, useEffect } from "react";
import { getMarkets, fetchGammaMarkets } from "./lib/api";
import { Market, MarketCategory, SortBy, SortDirection } from "./types/market";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MarketCard } from "./components/MarketCard";

function App() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCurrentOnly, setShowCurrentOnly] = useState(true);
  const [marketSource, setMarketSource] = useState<'clob' | 'gamma'>('gamma');
  const [category, setCategory] = useState<MarketCategory>();
  const [sortBy, setSortBy] = useState<SortBy>();
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');


  useEffect(() => {
    fetchMarkets();
  }, [marketSource, showCurrentOnly, category, sortBy, sortDirection]);

  async function fetchMarkets() {
    try {
      let data: Market[];
      if (marketSource === 'gamma') {
        data = await fetchGammaMarkets(showCurrentOnly);
        console.log('Fetched Gamma markets:', data);
      } else {
        data = await getMarkets(category, sortBy, sortDirection);
        console.log('Fetched CLOB markets:', data);
      }
      console.log('Setting markets state:', data);
      setMarkets(data || []);
      setError("");
    } catch (err) {
      setError("Failed to fetch markets. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-4">Polymarket Dashboard</h1>
        <div className="flex gap-4 mb-4">
          <button
            onClick={() => setMarketSource(marketSource === 'gamma' ? 'clob' : 'gamma')}
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            {marketSource === 'gamma' ? "Switch to CLOB" : "Switch to Gamma"}
          </button>
          <button
            onClick={() => setShowCurrentOnly(!showCurrentOnly)}
            className="px-4 py-2 bg-blue-500 text-white rounded"
          >
            {showCurrentOnly ? "Show All Markets" : "Show Current Markets"}
          </button>
          
          <Select value={category} onValueChange={(value) => setCategory(value as MarketCategory)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="sports">Sports</SelectItem>
              <SelectItem value="crypto">Crypto</SelectItem>
              <SelectItem value="politics">Politics</SelectItem>
              <SelectItem value="entertainment">Entertainment</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortBy)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="volume">Volume</SelectItem>
              <SelectItem value="created_at">Created Date</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sortDirection} onValueChange={(value) => setSortDirection(value as SortDirection)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort direction" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="asc">Ascending</SelectItem>
              <SelectItem value="desc">Descending</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="container mx-auto px-4">
        {(() => {
          console.log('Markets before filter:', markets);
          const filteredMarkets = markets.filter(market => {
            console.log('Filtering market:', market.id, market.is_active);
            return !showCurrentOnly || market.is_active;
          });
          console.log('Filtered markets:', filteredMarkets);
          return (
            <div 
              data-testid="market-grid" 
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {filteredMarkets.map((market) => {
                console.log('Rendering market:', market.id);
                return <MarketCard key={market.id} market={market} />;
              })}
            </div>
          );
        })()}
      </div>
    </div>
  )
}

export default App
