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

  return (
    <div className="w-full p-8 border border-gray-200 rounded-2xl bg-white hover:shadow-xl transition-all duration-300 hover:border-indigo-100">
      <div className="mb-8">
        <h3 className="text-xl font-bold text-gray-900 leading-relaxed hover:text-indigo-600 transition-colors">{market.question}</h3>
      </div>
      
      <div className="grid grid-cols-2 gap-8">
        <div className="p-6 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100 hover:border-indigo-100 transition-colors">
          <div className="text-sm font-semibold text-indigo-600 uppercase tracking-wide mb-2">Volume</div>
          <div className="text-3xl font-bold text-gray-900">{formatCurrency(market.volume || '0')}</div>
        </div>
        <div className="p-6 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100 hover:border-indigo-100 transition-colors">
          <div className="text-sm font-semibold text-indigo-600 uppercase tracking-wide mb-2">Open Interest</div>
          <div className="text-3xl font-bold text-gray-900">{formatCurrency(market.openInterest || '0')}</div>
        </div>
      </div>
      
      {market.description && (
        <div className="mt-8 text-sm text-gray-600 border-t border-gray-100 pt-6">
          {market.description.slice(0, 150)}...
        </div>
      )}
    </div>
  );
}
