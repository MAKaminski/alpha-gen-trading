"""Simple tests for time_utils module."""

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from alphagen.core.time_utils import (
    now_est, within_trading_window, session_bounds, next_session_open, to_est
)


class TestTimeUtilsSimple:
    """Simple tests for time_utils functions."""

    def test_now_est_returns_datetime(self):
        """Test now_est returns a datetime object."""
        result = now_est()
        assert isinstance(result, datetime)
        assert result.tzinfo == ZoneInfo('America/New_York')

    def test_to_est_with_utc_datetime(self):
        """Test to_est with UTC datetime."""
        utc_time = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = to_est(utc_time)
        
        assert result.tzinfo == ZoneInfo('America/New_York')
        # 14:30 UTC = 9:30 EST (winter time)
        assert result.hour == 9
        assert result.minute == 30

    def test_to_est_with_naive_datetime(self):
        """Test to_est with naive datetime (assumes EST)."""
        naive_time = datetime(2024, 1, 15, 14, 30, 0)
        result = to_est(naive_time)
        
        assert result.tzinfo == ZoneInfo('America/New_York')
        # Naive datetime is treated as EST, so 14:30 stays 14:30
        assert result.hour == 14
        assert result.minute == 30

    def test_to_est_with_est_datetime(self):
        """Test to_est with already EST datetime."""
        est_time = datetime(2024, 1, 15, 9, 30, 0, tzinfo=ZoneInfo('America/New_York'))
        result = to_est(est_time)
        
        assert result.tzinfo == ZoneInfo('America/New_York')
        assert result.hour == 9
        assert result.minute == 30

    @patch('alphagen.core.time_utils.now_est')
    def test_within_trading_window_during_market_hours(self, mock_now_est):
        """Test within_trading_window during market hours."""
        # Mock current time to be during market hours (10:30 AM EST) on a non-holiday
        market_time = datetime(2024, 1, 16, 10, 30, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_now_est.return_value = market_time
        
        result = within_trading_window()
        # The function uses SESSION_BUFFER, so we need to check if it's within the buffered window
        assert result is True

    @patch('alphagen.core.time_utils.now_est')
    def test_within_trading_window_before_market_hours(self, mock_now_est):
        """Test within_trading_window before market hours."""
        # Mock current time to be before market hours (8:00 AM EST) on a non-holiday
        before_market = datetime(2024, 1, 16, 8, 0, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_now_est.return_value = before_market
        
        result = within_trading_window()
        assert result is False

    @patch('alphagen.core.time_utils.now_est')
    def test_within_trading_window_after_market_hours(self, mock_now_est):
        """Test within_trading_window after market hours."""
        # Mock current time to be after market hours (5:00 PM EST) on a non-holiday
        after_market = datetime(2024, 1, 16, 17, 0, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_now_est.return_value = after_market
        
        result = within_trading_window()
        assert result is False

    @patch('alphagen.core.time_utils.now_est')
    def test_within_trading_window_weekend(self, mock_now_est):
        """Test within_trading_window on weekend."""
        # Mock current time to be Saturday (weekend)
        weekend_time = datetime(2024, 1, 13, 10, 30, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_now_est.return_value = weekend_time
        
        result = within_trading_window()
        # Weekend should return True (not a holiday, within buffered window)
        assert result is True

    def test_session_bounds_returns_tuple(self):
        """Test session_bounds returns a tuple of two datetimes."""
        result = session_bounds()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], datetime)
        assert isinstance(result[1], datetime)
        assert result[0] < result[1]

    def test_session_bounds_times_are_est(self):
        """Test session_bounds returns times in EST timezone."""
        result = session_bounds()
        assert result[0].tzinfo == ZoneInfo('America/New_York')
        assert result[1].tzinfo == ZoneInfo('America/New_York')

    def test_session_bounds_market_hours(self):
        """Test session_bounds returns correct market hours."""
        result = session_bounds()
        start_time, end_time = result
        
        # Market opens at 9:00 AM EST (with buffer)
        assert start_time.hour == 9
        assert start_time.minute == 0
        
        # Market closes at 4:30 PM EST (with buffer)
        assert end_time.hour == 16
        assert end_time.minute == 30

    @patch('alphagen.core.time_utils.US_MARKET_HOLIDAYS')
    @patch('alphagen.core.time_utils.session_bounds')
    @patch('alphagen.core.time_utils.now_est')
    def test_next_session_open_regular_day(self, mock_now_est, mock_session_bounds, mock_holidays):
        """Test next_session_open finds next regular trading day."""
        # Mock current time
        current_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_now_est.return_value = current_time

        # Mock holidays - next day is not a holiday
        mock_holidays.__contains__ = MagicMock(return_value=False)

        # Mock session bounds
        next_session_start = datetime(2024, 1, 16, 9, 0, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_session_bounds.return_value = (next_session_start, next_session_start + timedelta(hours=8))

        result = next_session_open()

        assert result == next_session_start
        mock_now_est.assert_called()
        mock_session_bounds.assert_called()

    @patch('alphagen.core.time_utils.US_MARKET_HOLIDAYS')
    @patch('alphagen.core.time_utils.session_bounds')
    @patch('alphagen.core.time_utils.now_est')
    def test_next_session_open_holiday_skipped(self, mock_now_est, mock_session_bounds, mock_holidays):
        """Test next_session_open skips holidays."""
        # Mock current time
        current_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_now_est.return_value = current_time

        # Mock holidays - next day is a holiday, day after is not
        def mock_holiday_check(date):
            return date == datetime(2024, 1, 16).date()
        mock_holidays.__contains__ = MagicMock(side_effect=mock_holiday_check)

        # Mock session bounds
        next_session_start = datetime(2024, 1, 17, 9, 0, 0, tzinfo=ZoneInfo('America/New_York'))
        mock_session_bounds.return_value = (next_session_start, next_session_start + timedelta(hours=8))

        result = next_session_open()

        assert result == next_session_start
        mock_now_est.assert_called()
        mock_session_bounds.assert_called()

    def test_now_est_timezone_consistency(self):
        """Test now_est always returns EST timezone."""
        result1 = now_est()
        result2 = now_est()
        
        assert result1.tzinfo == ZoneInfo('America/New_York')
        assert result2.tzinfo == ZoneInfo('America/New_York')

    def test_to_est_preserves_date(self):
        """Test to_est preserves the date component."""
        utc_time = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = to_est(utc_time)
        
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_session_bounds_same_day(self):
        """Test session_bounds returns times on the same day."""
        result = session_bounds()
        start_time, end_time = result
        
        assert start_time.date() == end_time.date()

    def test_within_trading_window_edge_cases(self):
        """Test within_trading_window edge cases."""
        with patch('alphagen.core.time_utils.now_est') as mock_now_est:
            # Test exactly at market open (with buffer, so 9:00 AM) on non-holiday
            market_open = datetime(2024, 1, 16, 9, 0, 0, tzinfo=ZoneInfo('America/New_York'))
            mock_now_est.return_value = market_open
            assert within_trading_window() is True
            
            # Test exactly at market close (with buffer, so 4:30 PM) on non-holiday
            market_close = datetime(2024, 1, 16, 16, 30, 0, tzinfo=ZoneInfo('America/New_York'))
            mock_now_est.return_value = market_close
            assert within_trading_window() is True
