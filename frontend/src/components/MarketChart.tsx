import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent } from "./ui/card";
import { getMarketOrders } from '../lib/api';

interface ChartData {
  date: string;
  openInterest: number;
}

interface MarketChartProps {
  marketId: string;
}

export function MarketChart({ marketId }: MarketChartProps) {
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchChartData() {
      try {
        const orders = await getMarketOrders(marketId);
        if (!orders?.data) {
          setError('No data available');
          return;
        }

        // Process orders to calculate open interest over time
        const processedData = orders.data
          .reduce((acc: { [key: string]: number }, order: any) => {
            const date = new Date(order.timestamp).toLocaleDateString();
            acc[date] = (acc[date] || 0) + Number(order.amount);
            return acc;
          }, {});

        // Convert to array format for chart
        const chartData: ChartData[] = Object.entries(processedData)
          .map(([date, openInterest]) => ({
            date,
            openInterest: Number(openInterest)
          }))
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

        setChartData(chartData);
        setError(null);
      } catch (err) {
        setError('Failed to load chart data');
        console.error('Error fetching market orders:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchChartData();
  }, [marketId]);

  if (loading) {
    return (
      <Card className="mt-4">
        <CardContent className="pt-6 flex justify-center items-center h-[300px]">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-600"></div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mt-4">
        <CardContent className="pt-6 flex justify-center items-center h-[300px] text-red-500">
          {error}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mt-4">
      <CardContent className="pt-6">
        <div style={{ width: '100%', height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <XAxis 
                dataKey="date"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                domain={['auto', 'auto']}
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => {
                  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
                  if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
                  return `$${value.toFixed(0)}`;
                }}
              />
              <Tooltip
                formatter={(value: number) => [`$${value.toLocaleString()}`, 'Open Interest']}
                labelFormatter={(label) => `Date: ${label}`}
              />
              <Line
                type="monotone"
                dataKey="openInterest"
                stroke="#9333ea"
                strokeWidth={2}
                dot={false}
                name="Open Interest"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
