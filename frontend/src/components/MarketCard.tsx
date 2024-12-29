import { Market } from "../types/market";

export function MarketCard({ market }: { market: Market }) {
  console.log('Rendering market:', market);
  const formatCurrency = (value: string) => {
    const num = parseFloat(value);
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  };

  const getStatusColor = (status: string, isActive: boolean) => {
    if (isActive) return 'bg-green-100 text-green-800';
    if (status === 'resolved') return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getDisplayStatus = (status: string, isActive: boolean) => {
    if (isActive) return 'Active';
    if (status === 'resolved') return 'Resolved';
    return status || 'Unknown';
  };

  return (
    <div className="w-full p-4 border rounded-lg shadow-sm bg-white hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold flex-grow">{market.question}</h3>
        <span className={`px-2 py-1 rounded text-sm ${getStatusColor(market.event_status, market.is_active)}`}>
          {getDisplayStatus(market.event_status, market.is_active)}
        </span>
      </div>
      
      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="text-sm font-medium text-gray-600">Volume</div>
          <div className="text-lg font-semibold">{formatCurrency(market.volume || '0')}</div>
        </div>
        <div>
          <div className="text-sm font-medium text-gray-600">Open Interest</div>
          <div className="text-lg font-semibold">{formatCurrency(market.open_interest || '0')}</div>
        </div>
        <div>
          <div className="text-sm font-medium text-gray-600">Traders</div>
          <div className="text-lg font-semibold">{market.trader_count?.toLocaleString() || 'N/A'}</div>
        </div>
      </div>
      
      <div className="mt-4">
        <span className={`px-2 py-1 rounded text-sm ${
          market.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
        }`}>
          {market.event_status || (market.is_active ? 'Active' : 'Inactive')}
        </span>
      </div>
    </div>
  );
}
