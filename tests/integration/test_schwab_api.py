"""Integration tests for Schwab API interactions."""
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from alphagen.schwab_oauth_client import SchwabOAuthClient


@pytest.mark.asyncio
async def test_schwab_oauth_client_creation():
    """Test Schwab OAuth client creation with mock token."""
    with patch('alphagen.schwab_oauth_client.client_from_token_file') as mock_client_from_token:
        mock_client = AsyncMock()
        mock_client_from_token.return_value = mock_client
        
        client = SchwabOAuthClient.create()
        
        assert client._client == mock_client
        mock_client_from_token.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_positions_with_mock_data():
    """Test fetching positions with mock Schwab API response."""
    with patch('alphagen.schwab_oauth_client.client_from_token_file') as mock_client_from_token:
        mock_client = AsyncMock()
        mock_client.get_account = AsyncMock(return_value={
            'securitiesAccount': {
                'positions': [
                    {
                        'instrument': {'symbol': 'QQQ'},
                        'longQuantity': 100,
                        'shortQuantity': 0,
                        'marketValue': 40000.0,
                        'averagePrice': 400.0
                    }
                ]
            }
        })
        mock_client_from_token.return_value = mock_client
        
        client = SchwabOAuthClient.create()
        positions = await client.fetch_positions()
        
        assert len(positions) == 1
        assert positions[0].symbol == 'QQQ'
        assert positions[0].quantity == 100
        assert positions[0].market_value == 40000.0


@pytest.mark.asyncio
async def test_fetch_positions_handles_response_object():
    """Test fetching positions when API returns Response object."""
    with patch('alphagen.schwab_oauth_client.client_from_token_file') as mock_client_from_token:
        mock_client = AsyncMock()
        
        # Mock Response object
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            'securitiesAccount': {
                'positions': []
            }
        }
        mock_client.get_account.return_value = mock_response
        
        mock_client_from_token.return_value = mock_client
        
        client = SchwabOAuthClient.create()
        positions = await client.fetch_positions()
        
        assert positions == []


@pytest.mark.asyncio
async def test_fetch_option_quote_success():
    """Test successful option quote fetching."""
    with patch('alphagen.schwab_oauth_client.client_from_token_file') as mock_client_from_token:
        mock_client = AsyncMock()
        mock_client.get_option_chain.return_value = {
            'callExpDateMap': {
                '2024-12-20:1': {
                    '400.0': [
                        {
                            'symbol': 'QQQ241220C00400000',
                            'strikePrice': 400.0,
                            'bid': 5.50,
                            'ask': 5.75,
                            'expirationDate': '2024-12-20T16:00:00Z'
                        }
                    ]
                }
            }
        }
        mock_client_from_token.return_value = mock_client
        
        client = SchwabOAuthClient.create()
        quote = await client.fetch_option_quote('QQQ241220C00400000')
        
        assert quote is not None
        assert quote.option_symbol == 'QQQ241220C00400000'
        assert quote.strike == 400.0
        assert quote.bid == 5.50
        assert quote.ask == 5.75


@pytest.mark.asyncio
async def test_fetch_option_quote_not_found():
    """Test option quote fetching when option not found."""
    with patch('alphagen.schwab_oauth_client.client_from_token_file') as mock_client_from_token:
        mock_client = AsyncMock()
        mock_client.get_option_chain.return_value = {
            'callExpDateMap': {}
        }
        mock_client_from_token.return_value = mock_client
        
        client = SchwabOAuthClient.create()
        quote = await client.fetch_option_quote('QQQ241220C00400000')
        
        assert quote is None


@pytest.mark.asyncio
async def test_submit_order_success():
    """Test successful order submission."""
    with patch('alphagen.schwab_oauth_client.client_from_token_file') as mock_client_from_token:
        mock_client = AsyncMock()
        mock_client.place_order.return_value = {'order_id': 'test_order_123'}
        mock_client_from_token.return_value = mock_client
        
        client = SchwabOAuthClient.create()
        
        from alphagen.core.events import TradeIntent
        intent = TradeIntent(
            as_of=datetime.now(timezone.utc),
            action="SELL_TO_OPEN",
            option_symbol="QQQ241220C00400000",
            quantity=25,
            limit_price=5.50,
            stop_loss=11.00,
            take_profit=2.75,
        )
        
        execution = await client.submit_order(intent)
        
        assert execution.order_id == 'test_order_123'
        assert execution.status == 'submitted'
        assert execution.intent == intent


@pytest.mark.asyncio
async def test_no_client_handling():
    """Test behavior when OAuth client is not available."""
    with patch('alphagen.schwab_oauth_client.client_from_token_file') as mock_client_from_token:
        mock_client_from_token.side_effect = Exception("No token file")
        
        client = SchwabOAuthClient.create()
        
        # Should return empty list for positions
        positions = await client.fetch_positions()
        assert positions == []
        
        # Should return None for option quotes
        quote = await client.fetch_option_quote('QQQ241220C00400000')
        assert quote is None
