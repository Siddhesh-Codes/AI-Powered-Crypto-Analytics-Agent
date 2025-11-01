"""
Historical Data Generator - Creates realistic price sequences from real snapshots
Uses random walk with drift to generate 60 days of historical data per cryptocurrency
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from database_manager import TrainingDataDB

class HistoricalDataGenerator:
    """Generate realistic historical price sequences"""
    
    def __init__(self, lookback_days=60):
        self.lookback_days = lookback_days
        self.db = TrainingDataDB()
    
    def generate_historical_sequences(self):
        """Generate historical data from database snapshots"""
        print("\n" + "="*70)
        print("📊 GENERATING HISTORICAL PRICE SEQUENCES")
        print("="*70 + "\n")
        
        # Load real crypto data from database
        crypto_data = self.db.get_all_crypto_data()
        
        if not crypto_data:
            print("⚠️  No crypto data found in database!")
            return None
        
        print(f"✅ Loaded {len(crypto_data)} real crypto snapshots from database")
        
        # Group by symbol and get latest snapshot for each
        df = pd.DataFrame(crypto_data)
        latest_prices = df.groupby('symbol').last().reset_index()
        
        print(f"✅ Found {len(latest_prices)} unique cryptocurrencies")
        print(f"   Generating {self.lookback_days} days of historical data per crypto...\n")
        
        all_sequences = []
        
        for idx, row in latest_prices.iterrows():
            symbol = row['symbol']
            current_price = row['price']
            volume = row.get('volume_24h', 1000000000)
            
            # Generate sequence
            sequence = self._generate_price_sequence(
                symbol=symbol,
                end_price=current_price,
                days=self.lookback_days,
                base_volume=volume
            )
            
            all_sequences.extend(sequence)
            
            if (idx + 1) % 10 == 0:
                print(f"   ✅ Generated sequences for {idx + 1}/{len(latest_prices)} cryptos")
        
        print(f"\n✅ Total historical data points generated: {len(all_sequences)}")
        
        # Convert to DataFrame
        historical_df = pd.DataFrame(all_sequences)
        
        # Save to CSV
        output_file = f"data/historical_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        historical_df.to_csv(output_file, index=False)
        print(f"💾 Historical data saved to: {output_file}")
        
        self.db.close()
        return historical_df
    
    def _generate_price_sequence(self, symbol, end_price, days, base_volume):
        """Generate realistic price sequence using random walk with drift"""
        
        # Market parameters based on crypto volatility
        daily_volatility = 0.05  # 5% daily volatility (realistic for crypto)
        drift = 0.001  # Slight upward drift
        
        # Generate random walk backwards from current price
        prices = [end_price]
        volumes = [base_volume]
        
        for i in range(days - 1):
            # Random daily return
            daily_return = np.random.normal(drift, daily_volatility)
            new_price = prices[-1] / (1 + daily_return)  # Work backwards
            
            # Volume variation (±30%)
            volume_change = np.random.uniform(0.7, 1.3)
            new_volume = volumes[-1] * volume_change
            
            prices.append(new_price)
            volumes.append(new_volume)
        
        # Reverse to get chronological order
        prices.reverse()
        volumes.reverse()
        
        # Create date range
        end_date = datetime.now()
        dates = [end_date - timedelta(days=days-1-i) for i in range(days)]
        
        # Create sequence data
        sequence = []
        for i in range(days):
            # Calculate daily metrics
            open_price = prices[i] * np.random.uniform(0.98, 1.02)
            high_price = max(prices[i], open_price) * np.random.uniform(1.0, 1.05)
            low_price = min(prices[i], open_price) * np.random.uniform(0.95, 1.0)
            close_price = prices[i]
            
            sequence.append({
                'date': dates[i].strftime('%Y-%m-%d'),
                'symbol': symbol,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volumes[i],
                'price': close_price  # For compatibility
            })
        
        return sequence
    
    def get_statistics(self, df):
        """Get statistics about generated data"""
        stats = {
            'total_records': len(df),
            'unique_symbols': df['symbol'].nunique(),
            'date_range': f"{df['date'].min()} to {df['date'].max()}",
            'avg_price': df['price'].mean(),
            'avg_volume': df['volume'].mean(),
            'price_volatility': df.groupby('symbol')['price'].std().mean()
        }
        return stats


if __name__ == "__main__":
    print("\n🚀 HISTORICAL DATA GENERATOR TEST\n")
    
    generator = HistoricalDataGenerator(lookback_days=60)
    historical_data = generator.generate_historical_sequences()
    
    if historical_data is not None:
        print("\n" + "="*70)
        print("📊 GENERATED DATA STATISTICS")
        print("="*70)
        stats = generator.get_statistics(historical_data)
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print("\n✅ Historical data generation complete!")
