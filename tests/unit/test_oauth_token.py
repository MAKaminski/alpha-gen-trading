"""Unit tests for OAuth token handling and refresh logic."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from src.alphagen.schwab_oauth_client import SchwabOAuthClient
from src.alphagen.core.events import EquityTick


class TestOAuthTokenHandling:
    """Test OAuth token validation, refresh, and error handling."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Schwab client."""
        mock_client = AsyncMock()
        mock_client.get_quote = AsyncMock()
        mock_client.ensure_valid_access_token = MagicMock()
        return mock_client

    @pytest.fixture
    def oauth_client(self, mock_client):
        """Create an OAuth client with mocked dependencies."""
        with patch(
            "src.alphagen.schwab_oauth_client.client_from_token_file"
        ) as mock_token_file:
            mock_token_file.return_value = mock_client
            client = SchwabOAuthClient.create()
            client._client = mock_client
            return client

    def test_token_validation_success(self, oauth_client, mock_client):
        """Test successful token validation."""
        # Mock successful token validation
        mock_client.ensure_valid_access_token.return_value = None

        result = oauth_client.is_token_valid()

        assert result is True
        mock_client.ensure_valid_access_token.assert_called_once()

    def test_token_validation_failure(self, oauth_client, mock_client):
        """Test token validation failure."""
        # Mock token validation failure
        mock_client.ensure_valid_access_token.side_effect = Exception("Token expired")

        result = oauth_client.is_token_valid()

        assert result is False

    def test_token_validation_no_client(self):
        """Test token validation when no client is available."""
        client = SchwabOAuthClient(None, "test_account")

        result = client.is_token_valid()

        assert result is False

    @pytest.mark.asyncio
    async def test_token_refresh_success(self, oauth_client, mock_client):
        """Test successful token refresh."""
        # Mock successful token refresh
        mock_client.ensure_valid_access_token.return_value = None

        result = await oauth_client._refresh_token_if_needed()

        assert result is True
        mock_client.ensure_valid_access_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_token_refresh_failure(self, oauth_client, mock_client):
        """Test token refresh failure."""
        # Mock token refresh failure
        mock_client.ensure_valid_access_token.side_effect = Exception("Refresh failed")

        result = await oauth_client._refresh_token_if_needed()

        assert result is False

    @pytest.mark.asyncio
    async def test_token_refresh_no_client(self):
        """Test token refresh when no client is available."""
        client = SchwabOAuthClient(None, "test_account")

        result = await client._refresh_token_if_needed()

        assert result is True  # Returns True when no client (no refresh needed)

    @pytest.mark.asyncio
    async def test_fetch_equity_quote_with_token_refresh(
        self, oauth_client, mock_client
    ):
        """Test equity quote fetching with token refresh."""
        # Mock successful token refresh and quote response
        mock_client.ensure_valid_access_token.return_value = None
        mock_client.get_quote = MagicMock(
            return_value={
                "QQQ": {
                    "quote": {"lastPrice": 400.0, "bidPrice": 399.5, "askPrice": 400.5}
                }
            }
        )

        result = await oauth_client.fetch_equity_quote("QQQ")

        assert result is not None
        assert isinstance(result, EquityTick)
        assert result.symbol == "QQQ"
        mock_client.ensure_valid_access_token.assert_called_once()
        mock_client.get_quote.assert_called_once_with("QQQ")

    @pytest.mark.asyncio
    async def test_fetch_equity_quote_token_refresh_failure(
        self, oauth_client, mock_client
    ):
        """Test equity quote fetching when token refresh fails."""
        # Mock token refresh failure
        mock_client.ensure_valid_access_token.side_effect = Exception(
            "Token refresh failed"
        )

        result = await oauth_client.fetch_equity_quote("QQQ")

        assert result is None
        mock_client.ensure_valid_access_token.assert_called_once()
        mock_client.get_quote.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_equity_quote_invalid_token_error(
        self, oauth_client, mock_client
    ):
        """Test equity quote fetching with InvalidTokenError."""
        # Mock token refresh success but API call fails with InvalidTokenError
        mock_client.ensure_valid_access_token.return_value = None
        mock_client.get_quote.side_effect = Exception("token_invalid: Invalid token")

        result = await oauth_client.fetch_equity_quote("QQQ")

        assert result is None
        mock_client.ensure_valid_access_token.assert_called_once()
        mock_client.get_quote.assert_called_once_with("QQQ")

    @pytest.mark.asyncio
    async def test_fetch_equity_quote_other_error(self, oauth_client, mock_client):
        """Test equity quote fetching with other errors."""
        # Mock token refresh success but API call fails with other error
        mock_client.ensure_valid_access_token.return_value = None
        mock_client.get_quote.side_effect = Exception("Network error")

        result = await oauth_client.fetch_equity_quote("QQQ")

        assert result is None
        mock_client.ensure_valid_access_token.assert_called_once()
        mock_client.get_quote.assert_called_once_with("QQQ")

    def test_save_token_success(self, oauth_client, mock_client):
        """Test successful token saving."""
        # Mock successful token saving
        mock_client.save_token = MagicMock()

        oauth_client.save_token("/path/to/token.json")

        mock_client.save_token.assert_called_once_with("/path/to/token.json")

    def test_save_token_no_client(self):
        """Test token saving when no client is available."""
        client = SchwabOAuthClient(None, "test_account")

        # Should not raise an exception
        client.save_token("/path/to/token.json")

    def test_save_token_no_save_method(self, oauth_client, mock_client):
        """Test token saving when client has no save_token method."""
        # Remove save_token method
        del mock_client.save_token

        # Should not raise an exception
        oauth_client.save_token("/path/to/token.json")


class TestOAuthClientCreation:
    """Test OAuth client creation scenarios."""

    def test_client_creation_with_valid_token(self):
        """Test client creation with valid token file."""
        with (
            patch(
                "src.alphagen.schwab_oauth_client.client_from_token_file"
            ) as mock_token_file,
            patch("src.alphagen.schwab_oauth_client.load_app_config") as mock_config,
        ):
            # Mock valid config
            mock_config.return_value.schwab.api_key = "test_key"
            mock_config.return_value.schwab.api_secret = "test_secret"
            mock_config.return_value.schwab.account_id = "test_account"
            mock_config.return_value.schwab.token_path = "test_token.json"

            # Mock token file exists and client creation succeeds
            with patch("pathlib.Path.exists", return_value=True):
                mock_client = AsyncMock()
                mock_token_file.return_value = mock_client

                client = SchwabOAuthClient.create()

                assert client is not None
                assert client._client == mock_client
                mock_token_file.assert_called_once()

    def test_client_creation_with_missing_config(self):
        """Test client creation with missing configuration."""
        with patch("src.alphagen.schwab_oauth_client.load_app_config") as mock_config:
            # Mock missing config
            mock_config.return_value.schwab.api_key = None
            mock_config.return_value.schwab.api_secret = None
            mock_config.return_value.schwab.account_id = None

            client = SchwabOAuthClient.create()

            assert client is None

    def test_client_creation_with_token_file_error(self):
        """Test client creation when token file loading fails."""
        with (
            patch(
                "src.alphagen.schwab_oauth_client.client_from_token_file"
            ) as mock_token_file,
            patch("src.alphagen.schwab_oauth_client.load_app_config") as mock_config,
        ):
            # Mock valid config
            mock_config.return_value.schwab.api_key = "test_key"
            mock_config.return_value.schwab.api_secret = "test_secret"
            mock_config.return_value.schwab.account_id = "test_account"
            mock_config.return_value.schwab.token_path = "test_token.json"

            # Mock token file exists but loading fails
            with patch("pathlib.Path.exists", return_value=True):
                mock_token_file.side_effect = Exception("Token file corrupted")

                client = SchwabOAuthClient.create()

                # Should return a client with None _client when token loading fails
                assert client is not None
                assert client._client is None
