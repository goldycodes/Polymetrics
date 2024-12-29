import { Market } from "../types/market";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface MarketStatsProps {
  markets: Market[];
  loading?: boolean;
}

export function MarketChart({ markets, loading = false }: MarketStatsProps) {
  if (loading) {
    return (
      <div className="p-4 border rounded animate-pulse">
        <div className="h-48 bg-gray-200 rounded"></div>
      </div>
    );
  }

  const totalVolume = markets.reduce((sum, market) => {
    const volume = parseFloat(market.volume || '0');
    return sum + (isNaN(volume) ? 0 : volume);
  }, 0);
  
  const totalOpenInterest = markets.reduce((sum, market) => {
    const openInterest = parseFloat(market.open_interest || '0');
    return sum + (isNaN(openInterest) ? 0 : openInterest);
  }, 0);
  
  const totalTraders = markets.reduce((sum, market) => {
    const traders = market.trader_count || (market.tokens?.length || 0);
    return sum + (isNaN(traders) ? 0 : traders);
  }, 0);

  // Format numbers for display
  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(2)}K`;
    return num.toFixed(2);
  };

  const data = [
    { name: 'Volume', value: totalVolume },
    { name: 'Open Interest', value: totalOpenInterest },
    { name: 'Traders', value: totalTraders }
  ];

  return (
    <div className="p-4 border rounded">
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <h4 className="text-sm text-gray-500">Volume</h4>
          <p className="text-lg font-semibold">${formatNumber(totalVolume)}</p>
        </div>
        <div className="text-center">
          <h4 className="text-sm text-gray-500">Open Interest</h4>
          <p className="text-lg font-semibold">${formatNumber(totalOpenInterest)}</p>
        </div>
        <div className="text-center">
          <h4 className="text-sm text-gray-500">Traders</h4>
          <p className="text-lg font-semibold">{totalTraders}</p>
        </div>
      </div>
      
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value: number) => `$${formatNumber(value)}`} />
            <Bar dataKey="value" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
