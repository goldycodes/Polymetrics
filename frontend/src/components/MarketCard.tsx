import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { TrendingUp, DollarSign, Users, LineChart } from "lucide-react";
import type { Market, Token } from "../types/market";
import { useState } from "react";
import { MarketChart } from "./MarketChart";

interface MarketCardProps {
  market: Market;
  onClick: () => void;
}

export function MarketCard({ market, onClick }: MarketCardProps) {
  const [showChart, setShowChart] = useState(false);
  const formatNumber = (num: number) => {
    if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `$${(num / 1000).toFixed(1)}K`;
    return `$${num.toFixed(0)}`;
  };

  return (
    <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={onClick}>
      <CardHeader>
        <CardTitle className="text-lg">{market.question}</CardTitle>
        <CardDescription className="line-clamp-2">{market.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="text-green-500" size={20} />
            {market.tokens.map((token: Token) => (
              <div key={token.outcome} className="flex items-center gap-1">
                <span className="font-medium">{token.outcome}:</span>
                <span>{(token.price * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
          
          <div className="grid grid-cols-3 gap-2">
            <div className="flex items-center gap-1">
              <DollarSign className="text-blue-500" size={16} />
              <div className="text-sm">
                <div className="font-medium">Volume</div>
                <div>{formatNumber(market.volume)}</div>
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              <LineChart className="text-purple-500" size={16} />
              <div className="text-sm">
                <div className="font-medium">Open Interest</div>
                <div>{formatNumber(market.open_interest)}</div>
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              <Users className="text-orange-500" size={16} />
              <div className="text-sm">
                <div className="font-medium">Traders</div>
                <div>{market.trader_count}</div>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-1">
            {/* Tags removed as they're not available in the current API */}
          </div>
          
          {showChart && <MarketChart marketId={market.id} />}
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowChart(!showChart);
            }}
            className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          >
            <LineChart size={16} />
            {showChart ? 'Hide Chart' : 'Show Chart'}
          </button>
        </div>
      </CardContent>
    </Card>
  );
}
