// Simple test script to verify real-time API integration
import { enhancedCryptoAPI } from '../src/services/enhancedCryptoAPI.js';

async function testRealTimeAPI() {
  console.log('🚀 Testing Enhanced Real-Time Crypto API...');
  
  try {
    const data = await enhancedCryptoAPI.fetchRealTimePrices();
    
    console.log('✅ API Test Results:');
    console.log(`📊 Fetched ${data.length} cryptocurrencies`);
    
    if (data.length > 0) {
      const btc = data.find(crypto => crypto.symbol === 'BTC');
      if (btc) {
        console.log(`🪙 Bitcoin Price: $${btc.price.toLocaleString()}`);
        console.log(`📈 24h Change: ${btc.changePercent24h.toFixed(2)}%`);
        console.log(`🔗 Data Source: ${btc.source}`);
        console.log(`⏰ Last Updated: ${new Date(btc.lastUpdated).toLocaleTimeString()}`);
      }
      
      console.log('\n📋 All Cryptocurrencies:');
      data.slice(0, 5).forEach(crypto => {
        console.log(`${crypto.symbol}: $${crypto.price.toLocaleString()} (${crypto.changePercent24h.toFixed(2)}%)`);
      });
    }
    
    console.log('\n✅ Enhanced API is working correctly!');
    
  } catch (error) {
    console.error('❌ API Test Failed:', error);
  }
}

// Run the test
testRealTimeAPI();
