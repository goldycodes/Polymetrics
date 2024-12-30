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

  const getStatusColor = (isActive?: boolean) => {
    return isActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
  };

  const getDisplayStatus = (isActive?: boolean) => {
    return isActive ? 'Active' : 'Inactive';
  };

  return (
    <div className="w-full p-6 border rounded-xl shadow-sm bg-white hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-6">
        <h3 className="text-xl font-bold text-gray-900 flex-grow pr-4">{market.question}</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(market.isActive)}`}>
          {getDisplayStatus(market.isActive)}
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-sm font-medium text-gray-500 mb-1">Volume</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(market.volume || '0')}</div>
        </div>
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="text-sm font-medium text-gray-500 mb-1">Open Interest</div>
          <div className="text-2xl font-bold text-gray-900">{formatCurrency(market.openInterest || '0')}</div>
        </div>
      </div>
      
      {market.description && (
        <div className="text-sm text-gray-600 border-t pt-4">
          {market.description.slice(0, 150)}...
        </div>
      )}
    </div>
  );
}
