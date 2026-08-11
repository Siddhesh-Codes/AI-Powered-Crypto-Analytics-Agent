import React, { useEffect, useRef } from 'react';

interface TradingViewWidgetProps {
  symbol?: string;
  width?: string;
  height?: string;
  interval?: string;
  theme?: 'light' | 'dark';
  style?: '1' | '2' | '3' | '8' | '9';
  locale?: string;
  toolbar_bg?: string;
  enable_publishing?: boolean;
  allow_symbol_change?: boolean;
  container_id?: string;
}

/**
 * TradingView Advanced Real-Time Chart Widget
 * Provides professional-grade real-time crypto charts
 */
export const TradingViewWidget: React.FC<TradingViewWidgetProps> = ({
  symbol = 'BINANCE:BTCUSDT',
  width = '100%',
  height = '400',
  interval = '5',
  theme = 'dark',
  style = '1',
  locale = 'en',
  toolbar_bg = '#f1f3f6',
  enable_publishing = false,
  allow_symbol_change = true,
  container_id = 'tradingview_widget'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    try {
      // Clear previous widget
      containerRef.current.innerHTML = '';

      // Create TradingView widget script
      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
      script.type = 'text/javascript';
      script.async = true;
      
      // Simplified configuration to avoid runtime errors
      const config = {
        autosize: true,
        symbol: symbol || 'BINANCE:BTCUSDT',
        interval: interval || '5',
        timezone: 'Etc/UTC',
        theme: theme || 'dark',
        style: style || '1',
        locale: locale || 'en',
        toolbar_bg: toolbar_bg || '#f1f3f6',
        enable_publishing: enable_publishing || false,
        allow_symbol_change: allow_symbol_change || true,
        calendar: false,
        support_host: 'https://www.tradingview.com'
      };

      script.innerHTML = JSON.stringify(config);
      containerRef.current.appendChild(script);
    } catch (error) {
      console.error('TradingView widget error:', error);
      if (containerRef.current) {
        containerRef.current.innerHTML = `
          <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #1e293b; color: #64748b; border-radius: 8px;">
            <div style="text-align: center;">
              <p>Chart temporarily unavailable</p>
              <button onclick="window.location.reload()" style="margin-top: 8px; padding: 4px 8px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer;">
                Reload
              </button>
            </div>
          </div>
        `;
      }
    }

    // Cleanup
    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbol, interval, theme, style, locale, toolbar_bg, enable_publishing, allow_symbol_change]);

  return (
    <div className="tradingview-widget-container w-full h-full" style={{ height, width, minHeight: height }}>
      <div 
        ref={containerRef}
        id={container_id}
        className="w-full h-full"
        style={{ height: '100%', width: '100%', minHeight: height }}
      />
      <div className="tradingview-widget-copyright">
        <a 
          href="https://www.tradingview.com/" 
          rel="noopener nofollow" 
          target="_blank"
          className="text-xs text-gray-500"
        >
          Track all markets on TradingView
        </a>
      </div>
    </div>
  );
};

/**
 * TradingView Mini Chart Widget
 * Compact real-time price widget
 */
interface TradingViewMiniProps {
  symbol?: string;
  width?: string;
  height?: string;
  colorTheme?: 'light' | 'dark';
}

export const TradingViewMiniWidget: React.FC<TradingViewMiniProps> = ({
  symbol = 'BINANCE:BTCUSDT',
  width = '100%',
  height = '200',
  colorTheme = 'dark'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.innerHTML = '';

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js';
      script.type = 'text/javascript';
      script.async = true;
      script.innerHTML = JSON.stringify({
        symbol: symbol,
        width: '100%',
        height: height,
        locale: 'en',
        dateRange: '12M',
        colorTheme: colorTheme,
        isTransparent: false,
        autosize: true,
        largeChartUrl: ''
      });

      containerRef.current.appendChild(script);
    }

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbol, height, colorTheme]);

  return (
    <div className="tradingview-widget-container" style={{ height, width }}>
      <div 
        ref={containerRef}
        style={{ height: '100%', width: '100%' }}
      />
    </div>
  );
};

/**
 * TradingView Market Overview Widget
 * Shows multiple crypto prices in real-time
 */
interface MarketOverviewProps {
  symbols?: string[];
  showSymbolLogo?: boolean;
  colorTheme?: 'light' | 'dark';
  isTransparent?: boolean;
  width?: string;
  height?: string;
}

export const TradingViewMarketOverview: React.FC<MarketOverviewProps> = ({
  symbols = [
    'BINANCE:BTCUSDT',
    'BINANCE:ETHUSDT', 
    'BINANCE:BNBUSDT',
    'BINANCE:SOLUSDT',
    'BINANCE:XRPUSDT',
    'BINANCE:ADAUSDT'
  ],
  showSymbolLogo = true,
  colorTheme = 'dark',
  isTransparent = false,
  width = '100%',
  height = '400'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.innerHTML = '';

      const script = document.createElement('script');
      script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js';
      script.type = 'text/javascript';
      script.async = true;
      script.innerHTML = JSON.stringify({
        colorTheme: colorTheme,
        dateRange: '12M',
        showChart: true,
        locale: 'en',
        width: '100%',
        height: height,
        largeChartUrl: '',
        isTransparent: isTransparent,
        showSymbolLogo: showSymbolLogo,
        showFloatingTooltip: false,
        plotLineColorGrowing: 'rgba(41, 98, 255, 1)',
        plotLineColorFalling: 'rgba(41, 98, 255, 1)',
        gridLineColor: 'rgba(240, 243, 250, 0)',
        scaleFontColor: 'rgba(106, 109, 120, 1)',
        belowLineFillColorGrowing: 'rgba(41, 98, 255, 0.12)',
        belowLineFillColorFalling: 'rgba(41, 98, 255, 0.12)',
        belowLineFillColorGrowingBottom: 'rgba(41, 98, 255, 0)',
        belowLineFillColorFallingBottom: 'rgba(41, 98, 255, 0)',
        symbolActiveColor: 'rgba(41, 98, 255, 0.12)',
        tabs: symbols.map(symbol => ({
          title: symbol.split(':')[1].replace('USDT', ''),
          symbols: [{ s: symbol }]
        }))
      });

      containerRef.current.appendChild(script);
    }

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbols, showSymbolLogo, colorTheme, isTransparent, height]);

  return (
    <div className="tradingview-widget-container" style={{ height, width }}>
      <div 
        ref={containerRef}
        style={{ height: '100%', width: '100%' }}
      />
    </div>
  );
};

export default TradingViewWidget;
