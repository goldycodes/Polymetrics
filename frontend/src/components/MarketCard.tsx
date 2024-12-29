import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Market } from "../types/market";
import { Calendar, DollarSign, Users, TrendingUp } from "lucide-react";
import { MarketChart } from "./MarketChart";

interface MarketCardProps {
  market: Market;
}

export function MarketCard({ market }: MarketCardProps) {
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString();
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  };

  const getStatusBadge = () => {
    if (market.active && market.accepting_orders) {
      return <Badge className="bg-green-500">Active</Badge>;
    }
    if (market.closed) {
      return <Badge variant="secondary">Closed</Badge>;
    }
    if (market.archived) {
      return <Badge variant="destructive">Archived</Badge>;
    }
    return <Badge variant="outline">Pending</Badge>;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg">{market.question}</CardTitle>
          {getStatusBadge()}
        </div>
        {(market.end_date_iso || market.game_start_time) && (
          <div className="flex items-center text-sm text-gray-500">
            <Calendar className="w-4 h-4 mr-2" />
            <span>
              {market.game_start_time
                ? `Game starts: ${formatDate(market.game_start_time)}`
                : `Ends: ${formatDate(market.end_date_iso)}`}
            </span>
          </div>
        )}
      </CardHeader>
      <CardContent>
        <CardDescription className="mb-4 line-clamp-2">
          {market.description}
        </CardDescription>
        
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="flex items-center">
            <DollarSign className="w-4 h-4 mr-2" />
            <div>
              <div className="text-sm font-medium">Volume</div>
              <div className="text-lg">{formatNumber(market.volume)}</div>
            </div>
          </div>
          <div className="flex items-center">
            <TrendingUp className="w-4 h-4 mr-2" />
            <div>
              <div className="text-sm font-medium">Open Interest</div>
              <div className="text-lg">{formatNumber(market.open_interest)}</div>
            </div>
          </div>
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-2" />
            <div>
              <div className="text-sm font-medium">Traders</div>
              <div className="text-lg">{market.trader_count}</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          {market.tokens.map((token) => (
            <div
              key={token.outcome}
              className="flex justify-between items-center p-2 bg-gray-50 rounded"
            >
              <span className="font-medium">{token.outcome}</span>
              <span className="text-sm">
                {(token.price * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>

        {market.open_interest_history.length > 0 && (
          <MarketChart
            data={market.open_interest_history}
            title="Open Interest History"
          />
        )}
      </CardContent>
    </Card>
  );
}
