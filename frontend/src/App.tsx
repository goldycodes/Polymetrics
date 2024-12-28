import { useState, useEffect } from "react";
import { getMarkets } from "./lib/api";
import { MarketCard } from "./components/MarketCard";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./components/ui/dialog";
import { ResponsiveContainer } from "recharts";
import { AlertCircle } from "lucide-react";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Market } from "./types/market";
import { MarketChart } from "./components/MarketChart";

function App() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [selectedMarket, setSelectedMarket] = useState<Market | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    fetchMarkets();
  }, []);

  async function fetchMarkets() {
    try {
      const data = await getMarkets();
      setMarkets(data || []);
      setError("");
    } catch (err) {
      setError("Failed to fetch markets. Please try again later.");
    } finally {
      setLoading(false);
    }
  }

  function handleMarketClick(market: Market) {
    setSelectedMarket(market);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Polymarket Dashboard</h1>
      
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {markets.map((market) => (
          <MarketCard
            key={market.id}
            market={market}
            onClick={() => handleMarketClick(market)}
          />
        ))}
      </div>

      <Dialog open={!!selectedMarket} onOpenChange={() => setSelectedMarket(null)}>
        {selectedMarket && (
          <DialogContent className="max-w-3xl">
            <DialogHeader>
              <DialogTitle>{selectedMarket.question}</DialogTitle>
            </DialogHeader>
            <div className="mt-4">
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <MarketChart marketId={selectedMarket.id} />
                </ResponsiveContainer>
              </div>
            </div>
          </DialogContent>
        )}
      </Dialog>
    </div>
  )
}

export default App
