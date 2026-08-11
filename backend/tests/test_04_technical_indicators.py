"""
Test Suite 4: Technical Indicators Tests
Tests RSI, MACD, Bollinger Bands, Moving Averages, Stochastic, Williams %R, ATR
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from technical_indicators import (
    TechnicalIndicators,
    analyze_technical_indicators,
    generate_trading_signals,
)


class TestRSI:
    """Test Relative Strength Index calculation"""

    def test_rsi_valid_output(self, sample_prices):
        """TC-4.1: RSI returns valid list of values"""
        result = TechnicalIndicators.calculate_rsi(sample_prices)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_rsi_range(self, sample_prices):
        """TC-4.2: RSI values are between 0 and 100"""
        result = TechnicalIndicators.calculate_rsi(sample_prices)
        for value in result:
            assert 0 <= value <= 100, f"RSI {value} is out of range [0, 100]"

    def test_rsi_insufficient_data(self):
        """TC-4.3: RSI returns empty list for insufficient data"""
        result = TechnicalIndicators.calculate_rsi([100, 105, 103])
        assert result == []

    def test_rsi_custom_period(self, sample_prices):
        """TC-4.4: RSI works with custom period"""
        result_7 = TechnicalIndicators.calculate_rsi(sample_prices, period=7)
        result_14 = TechnicalIndicators.calculate_rsi(sample_prices, period=14)
        assert len(result_7) > len(result_14)  # Shorter period = more values

    def test_rsi_uptrend(self):
        """TC-4.5: RSI is high (>50) for consistent uptrend"""
        uptrend = list(range(50, 100))  # 50 to 99 - consistent uptrend
        result = TechnicalIndicators.calculate_rsi(uptrend)
        if result:
            assert result[-1] > 50, f"RSI should be > 50 for uptrend, got {result[-1]}"


class TestMACD:
    """Test MACD calculation"""

    def test_macd_output_structure(self, sample_prices):
        """TC-4.6: MACD returns dict with correct keys"""
        result = TechnicalIndicators.calculate_macd(sample_prices)
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result

    def test_macd_values_present(self, sample_prices):
        """TC-4.7: MACD output contains values"""
        result = TechnicalIndicators.calculate_macd(sample_prices)
        assert len(result["macd"]) > 0
        assert len(result["signal"]) > 0
        assert len(result["histogram"]) > 0

    def test_macd_insufficient_data(self):
        """TC-4.8: MACD returns empty for insufficient data"""
        result = TechnicalIndicators.calculate_macd([100, 105, 103])
        assert result["macd"] == []
        assert result["signal"] == []
        assert result["histogram"] == []

    def test_macd_histogram_is_difference(self, sample_prices):
        """TC-4.9: MACD histogram ≈ MACD - Signal"""
        result = TechnicalIndicators.calculate_macd(sample_prices)
        if result["macd"] and result["signal"] and result["histogram"]:
            # Check last values (they should have same length after alignment)
            min_len = min(len(result["macd"]), len(result["signal"]), len(result["histogram"]))
            if min_len > 0:
                # Histogram = MACD - Signal (approximately)
                macd_val = result["macd"][-1]
                signal_val = result["signal"][-1]
                hist_val = result["histogram"][-1]
                assert abs(hist_val - (macd_val - signal_val)) < 0.01


class TestBollingerBands:
    """Test Bollinger Bands calculation"""

    def test_bollinger_output_structure(self, sample_prices):
        """TC-4.10: Bollinger Bands returns correct keys"""
        result = TechnicalIndicators.calculate_bollinger_bands(sample_prices)
        assert "upper" in result
        assert "middle" in result
        assert "lower" in result

    def test_bollinger_band_order(self, sample_prices):
        """TC-4.11: Upper band > Middle > Lower band"""
        result = TechnicalIndicators.calculate_bollinger_bands(sample_prices)
        if result["upper"] and result["middle"] and result["lower"]:
            for i in range(len(result["middle"])):
                assert result["upper"][i] >= result["middle"][i]
                assert result["middle"][i] >= result["lower"][i]

    def test_bollinger_insufficient_data(self):
        """TC-4.12: Bollinger returns empty for insufficient data"""
        result = TechnicalIndicators.calculate_bollinger_bands([100, 105])
        assert result["upper"] == []
        assert result["middle"] == []
        assert result["lower"] == []


class TestMovingAverages:
    """Test Moving Averages calculation"""

    def test_sma_default_periods(self, sample_prices):
        """TC-4.13: SMA calculates for default periods (20, 50, 200)"""
        result = TechnicalIndicators.calculate_moving_averages(sample_prices)
        assert "sma_20" in result
        assert "sma_50" in result
        assert "sma_200" in result

    def test_sma_20_has_values(self, sample_prices):
        """TC-4.14: SMA 20 returns values for 40-point dataset"""
        result = TechnicalIndicators.calculate_moving_averages(sample_prices)
        assert len(result["sma_20"]) > 0

    def test_sma_200_empty_for_short_data(self, sample_prices):
        """TC-4.15: SMA 200 is empty when data < 200 points"""
        result = TechnicalIndicators.calculate_moving_averages(sample_prices)
        assert result["sma_200"] == []

    def test_sma_empty_prices(self):
        """TC-4.16: Moving averages handles empty input"""
        result = TechnicalIndicators.calculate_moving_averages([])
        assert result == {}

    def test_sma_custom_periods(self, sample_prices):
        """TC-4.17: SMA works with custom periods"""
        result = TechnicalIndicators.calculate_moving_averages(sample_prices, periods=[5, 10])
        assert "sma_5" in result
        assert "sma_10" in result
        assert len(result["sma_5"]) > len(result["sma_10"])


class TestStochastic:
    """Test Stochastic Oscillator calculation"""

    def test_stochastic_output_structure(self, sample_ohlc_data):
        """TC-4.18: Stochastic returns K and D values"""
        highs = [d['high'] for d in sample_ohlc_data]
        lows = [d['low'] for d in sample_ohlc_data]
        closes = [d['close'] for d in sample_ohlc_data]
        result = TechnicalIndicators.calculate_stochastic(highs, lows, closes)
        assert "k" in result
        assert "d" in result

    def test_stochastic_range(self, sample_ohlc_data):
        """TC-4.19: Stochastic K values are between 0 and 100"""
        highs = [d['high'] for d in sample_ohlc_data]
        lows = [d['low'] for d in sample_ohlc_data]
        closes = [d['close'] for d in sample_ohlc_data]
        result = TechnicalIndicators.calculate_stochastic(highs, lows, closes)
        for k_val in result["k"]:
            assert 0 <= k_val <= 100, f"Stochastic K {k_val} is out of range"

    def test_stochastic_insufficient_data(self):
        """TC-4.20: Stochastic returns empty for insufficient data"""
        result = TechnicalIndicators.calculate_stochastic([100], [90], [95])
        assert result["k"] == []
        assert result["d"] == []


class TestWilliamsR:
    """Test Williams %R calculation"""

    def test_williams_r_range(self, sample_ohlc_data):
        """TC-4.21: Williams %R values are between -100 and 0"""
        highs = [d['high'] for d in sample_ohlc_data]
        lows = [d['low'] for d in sample_ohlc_data]
        closes = [d['close'] for d in sample_ohlc_data]
        result = TechnicalIndicators.calculate_williams_r(highs, lows, closes)
        for value in result:
            assert -100 <= value <= 0, f"Williams %R {value} is out of range"

    def test_williams_r_insufficient_data(self):
        """TC-4.22: Williams %R returns empty for insufficient data"""
        result = TechnicalIndicators.calculate_williams_r([100], [90], [95])
        assert result == []


class TestATR:
    """Test Average True Range calculation"""

    def test_atr_positive_values(self, sample_ohlc_data):
        """TC-4.23: ATR values are positive"""
        highs = [d['high'] for d in sample_ohlc_data]
        lows = [d['low'] for d in sample_ohlc_data]
        closes = [d['close'] for d in sample_ohlc_data]
        result = TechnicalIndicators.calculate_atr(highs, lows, closes)
        for value in result:
            assert value > 0, f"ATR should be positive, got {value}"

    def test_atr_insufficient_data(self):
        """TC-4.24: ATR returns empty for insufficient data"""
        result = TechnicalIndicators.calculate_atr([100], [90], [95])
        assert result == []


class TestTechnicalAnalysis:
    """Test the combined analysis function"""

    def test_analyze_technical_indicators(self, sample_ohlc_data):
        """TC-4.25: Full analysis returns all indicator types"""
        result = analyze_technical_indicators(sample_ohlc_data)
        assert "rsi" in result
        assert "macd" in result
        assert "bollinger_bands" in result
        assert "moving_averages" in result
        assert "stochastic" in result
        assert "williams_r" in result
        assert "atr" in result
        assert "signals" in result

    def test_analyze_empty_data(self):
        """TC-4.26: Analysis handles empty data gracefully"""
        result = analyze_technical_indicators([])
        assert "error" in result

    def test_trading_signals_structure(self, sample_ohlc_data):
        """TC-4.27: Trading signals have correct structure"""
        analysis = analyze_technical_indicators(sample_ohlc_data)
        signals = analysis["signals"]
        assert "overall_sentiment" in signals
        assert "strength" in signals
        assert "recommendations" in signals
        assert signals["overall_sentiment"] in ["bullish", "bearish", "neutral"]

    def test_trading_signals_recommendations(self, sample_ohlc_data):
        """TC-4.28: Trading signal recommendations have type and reason"""
        analysis = analyze_technical_indicators(sample_ohlc_data)
        for rec in analysis["signals"]["recommendations"]:
            assert "type" in rec
            assert rec["type"] in ["buy", "sell"]
            assert "reason" in rec
            assert "strength" in rec
