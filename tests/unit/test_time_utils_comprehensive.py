"""Comprehensive tests for time_utils module to achieve 100% coverage."""

from __future__ import annotations

from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta, time
from zoneinfo import ZoneInfo

from src.alphagen.core.time_utils import (
    now_est,
    within_trading_window,
    session_bounds,
    next_session_open,
    to_est,
)


class TestTimeUtilsComprehensive:
    """Comprehensive tests for time_utils functions to achieve 100% coverage."""

    def test_now_est_returns_current_time(self):
        """Test now_est returns current time in EST timezone."""
        result = now_est()
        assert isinstance(result, datetime)
        assert result.tzinfo == ZoneInfo("America/New_York")

        # Verify it's actually current time (within reasonable bounds)
        now_utc = datetime.now(timezone.utc)
        now_est_expected = now_utc.astimezone(ZoneInfo("America/New_York"))
        time_diff = abs((result - now_est_expected).total_seconds())
        assert time_diff < 5  # Should be within 5 seconds

    @patch("src.alphagen.core.time_utils.now_est")
    def test_within_trading_window_with_custom_moment(self, mock_now_est):
        """Test within_trading_window with custom moment parameter."""
        # Test during market hours on a non-holiday
        market_time = datetime(
            2024, 1, 16, 10, 30, 0, tzinfo=ZoneInfo("America/New_York")
        )
        result = within_trading_window(market_time)
        assert result is True
        mock_now_est.assert_not_called()

    @patch("src.alphagen.core.time_utils.now_est")
    def test_within_trading_window_with_none_moment(self, mock_now_est):
        """Test within_trading_window with None moment (uses now_est)."""
        market_time = datetime(
            2024, 1, 16, 10, 30, 0, tzinfo=ZoneInfo("America/New_York")
        )
        mock_now_est.return_value = market_time

        result = within_trading_window(None)
        assert result is True
        mock_now_est.assert_called_once()

    @patch("src.alphagen.core.time_utils.US_MARKET_HOLIDAYS")
    def test_within_trading_window_holiday(self, mock_holidays):
        """Test within_trading_window on a market holiday."""
        # Mock holiday check
        mock_holidays.__contains__ = MagicMock(return_value=True)

        market_time = datetime(
            2024, 1, 15, 10, 30, 0, tzinfo=ZoneInfo("America/New_York")
        )
        result = within_trading_window(market_time)
        assert result is False

    @patch("src.alphagen.core.time_utils.MARKET_OPEN", time(9, 0))
    @patch("src.alphagen.core.time_utils.MARKET_CLOSE", time(16, 0))
    @patch("src.alphagen.core.time_utils.SESSION_BUFFER", timedelta(minutes=30))
    @patch("src.alphagen.core.time_utils.US_MARKET_HOLIDAYS")
    def test_within_trading_window_buffer_timing(self, mock_holidays):
        """Test within_trading_window with session buffer timing."""
        mock_holidays.__contains__ = MagicMock(return_value=False)

        # Test exactly at buffer start (8:30 AM EST)
        buffer_start = datetime(
            2024, 1, 15, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
        )
        assert within_trading_window(buffer_start) is True

        # Test just before buffer (8:29 AM EST)
        before_buffer = datetime(
            2024, 1, 15, 8, 29, 0, tzinfo=ZoneInfo("America/New_York")
        )
        assert within_trading_window(before_buffer) is False

        # Test exactly at buffer end (4:30 PM EST)
        buffer_end = datetime(
            2024, 1, 15, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
        )
        assert within_trading_window(buffer_end) is True

        # Test just after buffer (4:31 PM EST)
        after_buffer = datetime(
            2024, 1, 15, 16, 31, 0, tzinfo=ZoneInfo("America/New_York")
        )
        assert within_trading_window(after_buffer) is False

    def test_session_bounds_with_custom_day(self):
        """Test session_bounds with custom day parameter."""
        custom_day = datetime(
            2024, 1, 15, 14, 30, 0, tzinfo=ZoneInfo("America/New_York")
        )
        result = session_bounds(custom_day)

        assert isinstance(result, tuple)
        assert len(result) == 2
        start_time, end_time = result

        # Both times should be on the same date as custom_day
        assert start_time.date() == custom_day.date()
        assert end_time.date() == custom_day.date()

        # Both times should be in EST
        assert start_time.tzinfo == ZoneInfo("America/New_York")
        assert end_time.tzinfo == ZoneInfo("America/New_York")

        # Start should be before end
        assert start_time < end_time

    @patch("src.alphagen.core.time_utils.now_est")
    def test_session_bounds_with_none_day(self, mock_now_est):
        """Test session_bounds with None day (uses now_est)."""
        current_time = datetime(
            2024, 1, 15, 14, 30, 0, tzinfo=ZoneInfo("America/New_York")
        )
        mock_now_est.return_value = current_time

        result = session_bounds(None)
        mock_now_est.assert_called_once()

        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch("src.alphagen.core.time_utils.MARKET_OPEN", time(9, 0))
    @patch("src.alphagen.core.time_utils.MARKET_CLOSE", time(16, 0))
    @patch("src.alphagen.core.time_utils.SESSION_BUFFER", timedelta(minutes=30))
    def test_session_bounds_exact_times(self):
        """Test session_bounds returns exact market times with buffer."""
        test_day = datetime(2024, 1, 15, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        start_time, end_time = session_bounds(test_day)

        # Start time should be 8:30 AM (9:00 AM - 30 min buffer)
        assert start_time.hour == 8
        assert start_time.minute == 30
        assert start_time.second == 0

        # End time should be 4:30 PM (4:00 PM + 30 min buffer)
        assert end_time.hour == 16
        assert end_time.minute == 30
        assert end_time.second == 0

    @patch("src.alphagen.core.time_utils.now_est")
    def test_next_session_open_with_custom_after(self, mock_now_est):
        """Test next_session_open with custom after parameter."""
        current_time = datetime(
            2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )
        mock_now_est.return_value = current_time

        with patch("src.alphagen.core.time_utils.session_bounds") as mock_bounds:
            # Mock session bounds to return next day's session
            next_session_start = datetime(
                2024, 1, 16, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
            )
            next_session_end = datetime(
                2024, 1, 16, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
            )
            mock_bounds.return_value = (next_session_start, next_session_end)

            with patch("src.alphagen.core.time_utils.US_MARKET_HOLIDAYS") as mock_holidays:
                mock_holidays.__contains__ = MagicMock(return_value=False)

                result = next_session_open(current_time)
                assert result == next_session_start
                mock_now_est.assert_not_called()  # Should not call now_est when after is provided

    @patch("src.alphagen.core.time_utils.now_est")
    def test_next_session_open_with_none_after(self, mock_now_est):
        """Test next_session_open with None after (uses now_est)."""
        current_time = datetime(
            2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )
        mock_now_est.return_value = current_time

        with patch("src.alphagen.core.time_utils.session_bounds") as mock_bounds:
            next_session_start = datetime(
                2024, 1, 16, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
            )
            next_session_end = datetime(
                2024, 1, 16, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
            )
            mock_bounds.return_value = (next_session_start, next_session_end)

            with patch("src.alphagen.core.time_utils.US_MARKET_HOLIDAYS") as mock_holidays:
                mock_holidays.__contains__ = MagicMock(return_value=False)

                result = next_session_open(None)
                # now_est is called twice: once as default parameter, once in the loop
                assert mock_now_est.call_count == 2
                assert result == next_session_start

    @patch("src.alphagen.core.time_utils.now_est")
    def test_next_session_open_multiple_holidays(self, mock_now_est):
        """Test next_session_open skips multiple consecutive holidays."""
        current_time = datetime(
            2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )
        mock_now_est.return_value = current_time

        with patch("src.alphagen.core.time_utils.session_bounds") as mock_bounds:
            # Mock multiple calls - first two days are holidays, third is not
            def mock_bounds_side_effect(probe_day):
                if probe_day.date() == datetime(2024, 1, 16).date():
                    return (
                        datetime(
                            2024, 1, 16, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
                        ),
                        datetime(
                            2024, 1, 16, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
                        ),
                    )
                elif probe_day.date() == datetime(2024, 1, 17).date():
                    return (
                        datetime(
                            2024, 1, 17, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
                        ),
                        datetime(
                            2024, 1, 17, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
                        ),
                    )
                else:
                    return (
                        datetime(
                            2024, 1, 18, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
                        ),
                        datetime(
                            2024, 1, 18, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
                        ),
                    )

            mock_bounds.side_effect = mock_bounds_side_effect

            with patch("src.alphagen.core.time_utils.US_MARKET_HOLIDAYS") as mock_holidays:

                def mock_holiday_check(date):
                    return date in [
                        datetime(2024, 1, 16).date(),
                        datetime(2024, 1, 17).date(),
                    ]

                mock_holidays.__contains__ = MagicMock(side_effect=mock_holiday_check)

                result = next_session_open(current_time)
                # Should return the third day (Jan 18) since first two are holidays
                assert result == datetime(
                    2024, 1, 18, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
                )

    @patch("src.alphagen.core.time_utils.now_est")
    def test_next_session_open_same_day_future_time(self, mock_now_est):
        """Test next_session_open when next session is later same day."""
        current_time = datetime(
            2024, 1, 15, 6, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )  # Before market
        mock_now_est.return_value = current_time

        with patch("src.alphagen.core.time_utils.session_bounds") as mock_bounds:
            # Same day session that starts later
            same_day_start = datetime(
                2024, 1, 15, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
            )
            same_day_end = datetime(
                2024, 1, 15, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
            )
            mock_bounds.return_value = (same_day_start, same_day_end)

            with patch("src.alphagen.core.time_utils.US_MARKET_HOLIDAYS") as mock_holidays:
                mock_holidays.__contains__ = MagicMock(return_value=False)

                result = next_session_open(current_time)
                assert result == same_day_start

    def test_to_est_with_utc_timestamp(self):
        """Test to_est with UTC timestamp."""
        utc_time = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = to_est(utc_time)

        assert result.tzinfo == ZoneInfo("America/New_York")
        # 14:30 UTC = 9:30 EST (winter time)
        assert result.hour == 9
        assert result.minute == 30
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_to_est_with_naive_timestamp(self):
        """Test to_est with naive timestamp (no timezone)."""
        naive_time = datetime(2024, 1, 15, 14, 30, 0)
        result = to_est(naive_time)

        assert result.tzinfo == ZoneInfo("America/New_York")
        # Naive time is treated as EST, so time stays the same
        assert result.hour == 14
        assert result.minute == 30

    def test_to_est_with_est_timestamp(self):
        """Test to_est with already EST timestamp."""
        est_time = datetime(2024, 1, 15, 9, 30, 0, tzinfo=ZoneInfo("America/New_York"))
        result = to_est(est_time)

        assert result.tzinfo == ZoneInfo("America/New_York")
        assert result.hour == 9
        assert result.minute == 30
        # Should be the same datetime object or equivalent
        assert result == est_time

    def test_to_est_with_custom_timezone(self):
        """Test to_est with custom timezone parameter."""
        pst_time = datetime(
            2024, 1, 15, 6, 30, 0, tzinfo=ZoneInfo("America/Los_Angeles")
        )
        result = to_est(pst_time, ZoneInfo("America/Los_Angeles"))

        assert result.tzinfo == ZoneInfo("America/New_York")
        # 6:30 PST = 9:30 EST
        assert result.hour == 9
        assert result.minute == 30

    def test_to_est_with_none_timezone(self):
        """Test to_est with None timezone parameter (uses default EST)."""
        utc_time = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
        result = to_est(utc_time, None)

        assert result.tzinfo == ZoneInfo("America/New_York")
        assert result.hour == 9
        assert result.minute == 30

    def test_to_est_preserves_microseconds(self):
        """Test to_est preserves microseconds."""
        utc_time = datetime(2024, 1, 15, 14, 30, 0, 123456, tzinfo=timezone.utc)
        result = to_est(utc_time)

        assert result.microsecond == 123456

    def test_to_est_preserves_date_components(self):
        """Test to_est preserves all date components."""
        utc_time = datetime(2024, 12, 25, 14, 30, 0, tzinfo=timezone.utc)
        result = to_est(utc_time)

        assert result.year == 2024
        assert result.month == 12
        assert result.day == 25
        assert result.hour == 9  # UTC to EST conversion
        assert result.minute == 30

    @patch("src.alphagen.core.time_utils.US_MARKET_HOLIDAYS")
    @patch("src.alphagen.core.time_utils.MARKET_OPEN", time(9, 0))
    @patch("src.alphagen.core.time_utils.MARKET_CLOSE", time(16, 0))
    @patch("src.alphagen.core.time_utils.SESSION_BUFFER", timedelta(minutes=30))
    def test_within_trading_window_comprehensive_timing(self, mock_holidays):
        """Test within_trading_window with comprehensive timing scenarios."""
        mock_holidays.__contains__ = MagicMock(return_value=False)

        base_date = datetime(2024, 1, 15)

        # Test various times throughout the day
        test_cases = [
            (base_date.replace(hour=8, minute=29), False, "Just before buffer"),
            (base_date.replace(hour=8, minute=30), True, "Exactly at buffer start"),
            (base_date.replace(hour=9, minute=0), True, "Market open"),
            (base_date.replace(hour=12, minute=0), True, "Market midday"),
            (base_date.replace(hour=15, minute=59), True, "Just before market close"),
            (base_date.replace(hour=16, minute=0), True, "Market close"),
            (base_date.replace(hour=16, minute=30), True, "Exactly at buffer end"),
            (base_date.replace(hour=16, minute=31), False, "Just after buffer"),
            (base_date.replace(hour=20, minute=0), False, "Evening"),
        ]

        for test_time, expected, description in test_cases:
            test_time = test_time.replace(tzinfo=ZoneInfo("America/New_York"))
            result = within_trading_window(test_time)
            assert result == expected, f"Failed for {description}: {test_time.time()}"

    def test_session_bounds_different_days(self):
        """Test session_bounds with different days."""
        test_dates = [
            datetime(
                2024, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("America/New_York")
            ),  # New Year's Day
            datetime(
                2024, 7, 4, 12, 0, 0, tzinfo=ZoneInfo("America/New_York")
            ),  # July 4th
            datetime(
                2024, 12, 25, 12, 0, 0, tzinfo=ZoneInfo("America/New_York")
            ),  # Christmas
        ]

        for test_date in test_dates:
            result = session_bounds(test_date)
            start_time, end_time = result

            # Both times should be on the same date
            assert start_time.date() == test_date.date()
            assert end_time.date() == test_date.date()

            # Both times should be in EST
            assert start_time.tzinfo == ZoneInfo("America/New_York")
            assert end_time.tzinfo == ZoneInfo("America/New_York")

    def test_now_est_timezone_consistency_multiple_calls(self):
        """Test now_est returns consistent timezone across multiple calls."""
        results = [now_est() for _ in range(5)]

        for result in results:
            assert result.tzinfo == ZoneInfo("America/New_York")
            assert isinstance(result, datetime)

        # All results should be recent (within 10 seconds of each other)
        time_diffs = [
            abs((results[i] - results[i - 1]).total_seconds())
            for i in range(1, len(results))
        ]
        for diff in time_diffs:
            assert diff < 10

    @patch("src.alphagen.core.time_utils.relativedelta")
    def test_next_session_open_uses_relativedelta(self, mock_relativedelta):
        """Test next_session_open uses relativedelta for day increment."""
        current_time = datetime(
            2024, 1, 15, 10, 0, 0, tzinfo=ZoneInfo("America/New_York")
        )

        with patch("src.alphagen.core.time_utils.now_est") as mock_now_est:
            mock_now_est.return_value = current_time

            with patch("src.alphagen.core.time_utils.session_bounds") as mock_bounds:
                next_session_start = datetime(
                    2024, 1, 16, 8, 30, 0, tzinfo=ZoneInfo("America/New_York")
                )
                next_session_end = datetime(
                    2024, 1, 16, 16, 30, 0, tzinfo=ZoneInfo("America/New_York")
                )
                mock_bounds.return_value = (next_session_start, next_session_end)

                with patch(
                    "src.alphagen.core.time_utils.US_MARKET_HOLIDAYS"
                ) as mock_holidays:
                    mock_holidays.__contains__ = MagicMock(return_value=False)

                    result = next_session_open(current_time)

                    # Verify relativedelta was called
                    mock_relativedelta.assert_called_with(days=1)
                    assert result == next_session_start
