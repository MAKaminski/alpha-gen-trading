"""Tests for time utilities module."""

from datetime import datetime
from zoneinfo import ZoneInfo
from freezegun import freeze_time

from alphagen.core.time_utils import (
    now_est,
    within_trading_window,
    session_bounds,
    next_session_open,
    to_est,
    US_MARKET_HOLIDAYS,
)
from alphagen.config import EST, MARKET_OPEN, MARKET_CLOSE, SESSION_BUFFER


class TestTimeUtils:
    """Test time utility functions."""

    def test_now_est_returns_datetime_with_est_timezone(self):
        """Test that now_est returns a datetime with EST timezone."""
        result = now_est()
        assert result.tzinfo == EST

    def test_within_trading_window_during_market_hours(self):
        """Test within_trading_window returns True during market hours."""
        # Test with 10 AM EST (within market hours)
        test_time = datetime(2024, 1, 16, 10, 0, 0, tzinfo=EST)
        result = within_trading_window(test_time)
        assert result is True

    def test_within_trading_window_after_market_hours(self):
        """Test within_trading_window returns False after market hours."""
        # Test with 10 PM EST (after market hours)
        test_time = datetime(2024, 1, 16, 22, 0, 0, tzinfo=EST)
        result = within_trading_window(test_time)
        assert result is False

    def test_within_trading_window_before_market_hours(self):
        """Test within_trading_window returns False before market hours."""
        # Test with 5 AM EST (before market hours)
        test_time = datetime(2024, 1, 16, 5, 0, 0, tzinfo=EST)
        result = within_trading_window(test_time)
        assert result is False

    def test_within_trading_window_on_holiday(self):
        """Test within_trading_window returns False on market holiday."""
        # Test with New Year's Day (holiday)
        test_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=EST)
        result = within_trading_window(test_time)
        assert result is False

    def test_within_trading_window_with_custom_moment(self):
        """Test within_trading_window with custom moment parameter."""
        custom_moment = datetime(2024, 1, 16, 14, 0, 0, tzinfo=EST)
        result = within_trading_window(custom_moment)
        assert result is True

    @freeze_time("2024-01-16 10:00:00", tz_offset=-5)
    def test_session_bounds_returns_correct_bounds(self):
        """Test session_bounds returns correct start and end times."""
        start, end = session_bounds()

        expected_start = (
            datetime.combine(datetime(2024, 1, 16).date(), MARKET_OPEN, tzinfo=EST)
            - SESSION_BUFFER
        )
        expected_end = (
            datetime.combine(datetime(2024, 1, 16).date(), MARKET_CLOSE, tzinfo=EST)
            + SESSION_BUFFER
        )

        assert start == expected_start
        assert end == expected_end

    @freeze_time("2024-01-16 10:00:00", tz_offset=-5)
    def test_session_bounds_with_custom_day(self):
        """Test session_bounds with custom day parameter."""
        custom_day = datetime(2024, 1, 16, 10, 0, 0, tzinfo=EST)
        start, end = session_bounds(custom_day)

        expected_start = (
            datetime.combine(datetime(2024, 1, 16).date(), MARKET_OPEN, tzinfo=EST)
            - SESSION_BUFFER
        )
        expected_end = (
            datetime.combine(datetime(2024, 1, 16).date(), MARKET_CLOSE, tzinfo=EST)
            + SESSION_BUFFER
        )

        assert start == expected_start
        assert end == expected_end

    @freeze_time("2024-01-16 22:00:00", tz_offset=-5)  # After market close
    def test_next_session_open_skips_holidays(self):
        """Test next_session_open skips market holidays."""
        result = next_session_open()

        # Should be next trading day (Wednesday) session start (with buffer)
        assert result.date() == datetime(2024, 1, 17).date()
        assert result.hour == 9  # 9:30 AM - 30 min buffer = 9:00 AM
        assert result.minute == 0
        assert result.tzinfo == EST

    @freeze_time("2024-01-01 10:00:00", tz_offset=-5)  # New Year's Day (holiday)
    def test_next_session_open_from_holiday(self):
        """Test next_session_open from a holiday."""
        result = next_session_open()

        # Should skip the holiday and return next trading day session start (with buffer)
        assert result.date() > datetime(2024, 1, 1).date()
        assert result.hour == 9  # 9:30 AM - 30 min buffer = 9:00 AM
        assert result.minute == 0

    @freeze_time("2024-01-16 10:00:00", tz_offset=-5)
    def test_next_session_open_with_custom_after(self):
        """Test next_session_open with custom after parameter."""
        custom_after = datetime(2024, 1, 16, 14, 0, 0, tzinfo=EST)
        result = next_session_open(custom_after)

        # Should be next trading day
        assert result.date() == datetime(2024, 1, 17).date()
        assert result > custom_after

    def test_to_est_with_naive_datetime(self):
        """Test to_est with naive datetime."""
        naive_dt = datetime(2024, 1, 15, 10, 0, 0)
        result = to_est(naive_dt)

        assert result.tzinfo == EST
        assert result.replace(tzinfo=None) == naive_dt

    def test_to_est_with_timezone_aware_datetime(self):
        """Test to_est with timezone-aware datetime."""
        utc_dt = datetime(2024, 1, 15, 15, 0, 0, tzinfo=ZoneInfo("UTC"))
        result = to_est(utc_dt)

        assert result.tzinfo == EST
        # Should convert from UTC to EST (UTC-5)
        assert result.hour == 10  # 15:00 UTC = 10:00 EST

    def test_to_est_with_custom_timezone(self):
        """Test to_est with custom timezone parameter."""
        pst_dt = datetime(2024, 1, 15, 7, 0, 0, tzinfo=ZoneInfo("US/Pacific"))
        result = to_est(pst_dt, ZoneInfo("US/Pacific"))

        assert result.tzinfo == EST
        # PST is UTC-8, EST is UTC-5, so 7 AM PST = 10 AM EST
        assert result.hour == 10

    def test_us_market_holidays_includes_known_holidays(self):
        """Test that US_MARKET_HOLIDAYS includes known market holidays."""
        # Test New Year's Day
        assert datetime(2024, 1, 1).date() in US_MARKET_HOLIDAYS
        # Test Independence Day
        assert datetime(2024, 7, 4).date() in US_MARKET_HOLIDAYS
        # Test Christmas Day
        assert datetime(2024, 12, 25).date() in US_MARKET_HOLIDAYS

    def test_us_market_holidays_excludes_regular_weekdays(self):
        """Test that US_MARKET_HOLIDAYS excludes regular weekdays."""
        # Test regular Tuesday (not a holiday)
        assert datetime(2024, 1, 16).date() not in US_MARKET_HOLIDAYS
        # Test regular Wednesday (not a holiday)
        assert datetime(2024, 1, 17).date() not in US_MARKET_HOLIDAYS
