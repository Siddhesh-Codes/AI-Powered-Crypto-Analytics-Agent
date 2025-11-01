import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Price Chart Component
 * Displays price history as a line chart
 */
interface PriceChartProps {
  data: { timestamp: number; price: number }[];
  symbol: string;
  timeframe: string;
  className?: string;
}

export const PriceChart: React.FC<PriceChartProps> = ({ 
  data = [], 
  symbol = '', 
  timeframe = '24h', 
  className = '' 
}) => {
  // Add null safety for data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className={`flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">No price data available</p>
      </div>
    );
  }

  // Validate price data - check for unrealistic price ranges
  const prices = data.map(item => item?.price || 0).filter(price => price > 0);
  if (prices.length === 0) {
    return (
      <div className={`flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">Invalid price data</p>
      </div>
    );
  }

  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice;
  const avgPrice = prices.reduce((sum, price) => sum + price, 0) / prices.length;

  // Temporarily disable price validation to allow all data through
  // if (minPrice < 0.01 && maxPrice > avgPrice * 10) {
  //   console.warn(`Extremely unrealistic price data detected for ${symbol}:`, { minPrice, maxPrice, avgPrice });
  //   return (
  //     <div className={`flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}>
  //       <p className="text-gray-500 dark:text-gray-400">Loading accurate price data...</p>
  //     </div>
  //   );
  // }

  // Debug log to see price data
  console.log(`PriceChart for ${symbol}:`, {
    dataLength: data.length,
    firstPrice: data[0]?.price,
    lastPrice: data[data.length - 1]?.price,
    minPrice,
    maxPrice,
    avgPrice: avgPrice.toFixed(2)
  });

  const chartData = {
    labels: data.map(item => {
      if (!item || typeof item.timestamp !== 'number') return '';
      const date = new Date(item.timestamp);
      if (timeframe === '1h') {
        return date.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Kolkata',
          hour12: true
        }).replace(/am/i, 'AM').replace(/pm/i, 'PM');
      } else if (timeframe === '24h') {
        return date.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          timeZone: 'Asia/Kolkata',
          hour12: true
        }).replace(/am/i, 'AM').replace(/pm/i, 'PM');
      } else {
        return date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric',
          timeZone: 'Asia/Kolkata'
        });
      }
    }),
    datasets: [
      {
        label: `${symbol || 'Crypto'} Price`,
        data: data.map(item => (item && typeof item.price === 'number') ? item.price : 0),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        borderWidth: 1,
        callbacks: {
          title: function(context: any) {
            // Show time in IST timezone
            const dataIndex = context[0].dataIndex;
            const timestamp = data[dataIndex]?.timestamp;
            if (timestamp) {
              const date = new Date(timestamp);
              return date.toLocaleTimeString('en-US', {
                timeZone: 'Asia/Kolkata',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
              }).replace(/am/i, 'AM').replace(/pm/i, 'PM');
            }
            return '';
          },
          label: function(context: any) {
            return `${symbol}: $${context.parsed.y.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}`;
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: 'rgb(148, 163, 184)',
          maxTicksLimit: 8,
        },
      },
      y: {
        display: true,
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: 'rgb(148, 163, 184)',
          callback: function(value: any) {
            return '$' + value.toLocaleString();
          },
        },
      },
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
  };

  return (
    <div className={`${className}`}>
      <Line 
        data={chartData} 
        options={options} 
        key={`price-chart-${symbol}-${data.length}-${data[0]?.timestamp || 'no-data'}`} // Force re-render with unique key
      />
    </div>
  );
};

/**
 * Volume Chart Component
 * Displays trading volume as a bar chart
 */
interface VolumeChartProps {
  data: { timestamp: number; volume: number }[];
  symbol: string;
  className?: string;
}

export const VolumeChart: React.FC<VolumeChartProps> = ({ 
  data = [], 
  symbol = '', 
  className = '' 
}) => {
  // Add null safety for data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className={`flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">No volume data available</p>
      </div>
    );
  }

  const chartData = {
    labels: data.map(item => {
      if (!item || typeof item.timestamp !== 'number') return '';
      const date = new Date(item.timestamp);
      // For 24h data, show time instead of date
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        timeZone: 'Asia/Kolkata',
        hour12: true
      }).replace(/am/i, 'AM').replace(/pm/i, 'PM');
    }),
    datasets: [
      {
        label: `${symbol || 'Crypto'} Volume`,
        data: data.map(item => (item && typeof item.volume === 'number') ? item.volume : 0),
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        borderWidth: 1,
        callbacks: {
          title: function(context: any) {
            // Show time in IST timezone
            const dataIndex = context[0].dataIndex;
            const timestamp = data[dataIndex]?.timestamp;
            if (timestamp) {
              const date = new Date(timestamp);
              return date.toLocaleTimeString('en-US', {
                timeZone: 'Asia/Kolkata',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
              }).replace(/am/i, 'AM').replace(/pm/i, 'PM');
            }
            return '';
          },
          label: function(context: any) {
            return `${symbol} Volume: ${(context.parsed.y / 1000000).toFixed(2)}M`;
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: 'rgb(148, 163, 184)',
          maxTicksLimit: 8, // Limit number of ticks to avoid clutter
        },
      },
      y: {
        display: true,
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: 'rgb(148, 163, 184)',
          callback: function(value: any) {
            return (value / 1000000).toFixed(0) + 'M';
          },
        },
      },
    },
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
  };

  return (
    <div className={`${className}`}>
      <Bar data={chartData} options={options} />
    </div>
  );
};

/**
 * Portfolio Allocation Chart
 * Displays portfolio allocation as a doughnut chart
 */
interface PortfolioChartProps {
  data: { symbol: string; value: number; percentage: number }[];
  className?: string;
}

export const PortfolioChart: React.FC<PortfolioChartProps> = ({ 
  data, 
  className = '' 
}) => {
  const colors = [
    'rgb(34, 197, 94)',   // Green
    'rgb(59, 130, 246)',  // Blue
    'rgb(245, 158, 11)',  // Yellow
    'rgb(239, 68, 68)',   // Red
    'rgb(168, 85, 247)',  // Purple
    'rgb(236, 72, 153)',  // Pink
    'rgb(14, 165, 233)',  // Sky
    'rgb(132, 204, 22)',  // Lime
  ];

  const chartData = {
    labels: data.map(item => item.symbol),
    datasets: [
      {
        data: data.map(item => item.percentage),
        backgroundColor: colors.slice(0, data.length),
        borderColor: colors.slice(0, data.length).map(color => color.replace('rgb', 'rgba').replace(')', ', 0.8)')),
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: 'rgb(148, 163, 184)',
          usePointStyle: true,
          padding: 20,
          generateLabels: function(chart: any) {
            const dataset = chart.data.datasets[0];
            return chart.data.labels.map((label: string, i: number) => ({
              text: `${label} (${dataset.data[i].toFixed(1)}%)`,
              fillStyle: dataset.backgroundColor[i],
              strokeStyle: dataset.borderColor[i],
              lineWidth: dataset.borderWidth,
              pointStyle: 'circle',
              index: i,
            }));
          },
        },
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        borderWidth: 1,
        callbacks: {
          label: function(context: any) {
            const item = data[context.dataIndex];
            return [
              `${item.symbol}: ${item.percentage.toFixed(1)}%`,
              `Value: $${item.value.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}`
            ];
          },
        },
      },
    },
    cutout: '60%',
  };

  return (
    <div className={`${className}`}>
      <Doughnut data={chartData} options={options} />
    </div>
  );
};

/**
 * Market Overview Chart
 * Displays top cryptocurrencies by market cap
 */
interface MarketOverviewChartProps {
  data: { symbol: string; marketCap: number; change24h: number }[];
  className?: string;
}

export const MarketOverviewChart: React.FC<MarketOverviewChartProps> = ({ 
  data = [], 
  className = '' 
}) => {
  // Add null safety for data
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className={`flex items-center justify-center h-80 bg-gray-50 dark:bg-gray-800 rounded-lg ${className}`}>
        <p className="text-gray-500 dark:text-gray-400">No market data available</p>
      </div>
    );
  }

  const formatMarketCap = (value: number) => {
    const safeValue = value || 0;
    if (safeValue >= 1e12) {
      return `$${(safeValue / 1e12).toFixed(2)}T`;
    } else if (safeValue >= 1e9) {
      return `$${(safeValue / 1e9).toFixed(2)}B`;
    } else if (safeValue >= 1e6) {
      return `$${(safeValue / 1e6).toFixed(2)}M`;
    } else {
      return `$${safeValue.toLocaleString()}`;
    }
  };

  const chartData = {
    labels: data.map(item => item?.symbol || 'N/A'),
    datasets: [
      {
        label: 'Market Cap',
        data: data.map(item => (item?.marketCap || 0) / 1000000000), // Convert to billions for consistent display
        backgroundColor: data.map(item => 
          (item?.change24h || 0) >= 0 ? 'rgba(34, 197, 94, 0.6)' : 'rgba(239, 68, 68, 0.6)'
        ),
        borderColor: data.map(item => 
          (item?.change24h || 0) >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'
        ),
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0, // Remove animations for stable display
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(71, 85, 105, 0.5)',
        borderWidth: 1,
        callbacks: {
          label: function(context: any) {
            const item = data[context.dataIndex];
            return [
              `Market Cap: ${formatMarketCap(item.marketCap)}`,
              `24h Change: ${item.change24h >= 0 ? '+' : ''}${item.change24h.toFixed(2)}%`
            ];
          },
        },
      },
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: 'rgb(148, 163, 184)',
        },
      },
      y: {
        display: true,
        grid: {
          color: 'rgba(71, 85, 105, 0.3)',
        },
        ticks: {
          color: 'rgb(148, 163, 184)',
          callback: function(value: any) {
            return '$' + value.toFixed(0) + 'B';
          },
        },
      },
    },
  };

  return (
    <div className={`${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">Market Capitalization Overview</h3>
        <div className="text-sm text-slate-400">
          Updated daily • Last update: {new Date().toLocaleDateString('en-US', {
            timeZone: 'Asia/Kolkata',
            day: 'numeric',
            month: 'short',
            year: 'numeric'
          })}
        </div>
      </div>
      <div className="mb-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {data.slice(0, 8).map((item, index) => (
            <div 
              key={item.symbol} 
              className="bg-slate-700 p-3 rounded-lg text-center"
            >
              <div className="text-sm font-medium text-slate-200 mb-1">
                {item.symbol}
              </div>
              <div className="text-lg font-bold text-white mb-1">
                {formatMarketCap(item.marketCap)}
              </div>
              <div className={`text-sm ${
                item.change24h >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {item.change24h >= 0 ? '+' : ''}{item.change24h.toFixed(2)}%
              </div>
            </div>
          ))}
        </div>
      </div>
      <Bar data={chartData} options={options} />
    </div>
  );
};
