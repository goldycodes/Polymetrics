import { Market } from "../types/market";

export function MarketCard({ market }: { market: Market }) {
  console.log('Rendering market:', market);
  const formatNumber = (value: string | null | undefined) => {
    if (!value) return 'N/A';
    const num = parseFloat(value);
    if (isNaN(num)) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(num);
  };

  return (
    <div className="w-full p-4 border rounded-lg shadow-sm bg-white">
      <div className="mb-4">
        <div className="flex justify-between items-start">
          <h3 className="text-lg font-semibold">{market.question}</h3>
          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
            market.is_active
              ? 'bg-green-500 text-white'
              : market.event_status === 'resolved'
              ? 'bg-gray-200 text-gray-700'
              : 'bg-gray-100 text-gray-600'
          }`}>
            {market.is_active
              ? 'Active'
              : market.event_status === 'resolved'
              ? 'Resolved'
              : 'Inactive'}
          </span>
        </div>
        <p className="mt-2 text-sm text-gray-600">{market.description}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="text-sm font-medium">Volume</div>
          <div className="text-lg">{formatNumber(market.volume)}</div>
        </div>
        <div>
          <div className="text-sm font-medium">Open Interest</div>
          <div className="text-lg">{formatNumber(market.open_interest)}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {market.tokens.map((token) => (
          <div
            key={token.token_id}
            className="flex justify-between items-center p-2 bg-gray-50 rounded"
          >
            <span className="font-medium">{token.name}</span>
            <span className="text-sm">
              {(parseFloat(token.price) * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
