import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CryptoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'Slone_cryptoBuddy/1.0'
        })

    def _make_request(self, endpoint, params=None):
        try:
            response = self.session.get(f"{self.BASE_URL}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None

    def get_coin_data(self, coin_id: str) -> Optional[Dict]:
        """Fetch real-time data for a specific cryptocurrency."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/coins/{coin_id}",
                params={
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'true',
                    'community_data': 'false',
                    'developer_data': 'false'
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching data for {coin_id}: {str(e)}")
            return None

    def get_market_data(self):
        try:
            # Get global market data
            global_data = self._make_request("global")
            if not global_data:
                return {
                    'total_market_cap': 0,
                    'total_volume': 0,
                    'btc_dominance': 0,
                    'coins': []
                }

            # Get top coins data
            coins_data = self._make_request("coins/markets", {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 10,
                'page': 1,
                'sparkline': False
            })

            if not coins_data:
                return {
                    'total_market_cap': 0,
                    'total_volume': 0,
                    'btc_dominance': 0,
                    'coins': []
                }

            # Format the response
            return {
                'total_market_cap': global_data['data']['total_market_cap']['usd'],
                'total_volume': global_data['data']['total_volume']['usd'],
                'btc_dominance': global_data['data']['market_cap_percentage']['btc'],
                'coins': [{
                    'id': coin['id'],
                    'symbol': coin['symbol'],
                    'name': coin['name'],
                    'current_price': coin['current_price'],
                    'market_cap': coin['market_cap'],
                    'price_change_percentage_24h': coin['price_change_percentage_24h'],
                    'total_volume': coin['total_volume']
                } for coin in coins_data]
            }
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return {
                'total_market_cap': 0,
                'total_volume': 0,
                'btc_dominance': 0,
                'coins': []
            }

    def get_global_data(self) -> Optional[Dict]:
        """Fetch global cryptocurrency market data."""
        try:
            response = self.session.get(f"{self.BASE_URL}/global")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching global data: {str(e)}")
            return None

    def get_trending_coins(self):
        try:
            trending_data = self._make_request("search/trending")
            if not trending_data:
                return []

            return [{
                'id': coin['item']['id'],
                'symbol': coin['item']['symbol'],
                'name': coin['item']['name'],
                'market_cap_rank': coin['item']['market_cap_rank'],
                'price_change_percentage_24h': coin['item']['price_change_percentage_24h']
            } for coin in trending_data['coins']]
        except Exception as e:
            logger.error(f"Error getting trending coins: {str(e)}")
            return []

    def get_coin_history(self, coin_id, days=30):
        try:
            history_data = self._make_request(f"coins/{coin_id}/market_chart", {
                'vs_currency': 'usd',
                'days': days
            })
            if not history_data:
                return None

            return {
                'prices': history_data['prices'],
                'market_caps': history_data['market_caps'],
                'total_volumes': history_data['total_volumes']
            }
        except Exception as e:
            logger.error(f"Error getting coin history: {str(e)}")
            return None

    def get_coin_info(self, coin_id):
        try:
            coin_data = self._make_request(f"coins/{coin_id}")
            if not coin_data:
                return None

            return {
                'id': coin_data['id'],
                'symbol': coin_data['symbol'],
                'name': coin_data['name'],
                'description': coin_data['description']['en'],
                'current_price': coin_data['market_data']['current_price']['usd'],
                'market_cap': coin_data['market_data']['market_cap']['usd'],
                'price_change_percentage_24h': coin_data['market_data']['price_change_percentage_24h'],
                'total_volume': coin_data['market_data']['total_volume']['usd'],
                'circulating_supply': coin_data['market_data']['circulating_supply'],
                'total_supply': coin_data['market_data']['total_supply'],
                'max_supply': coin_data['market_data']['max_supply']
            }
        except Exception as e:
            logger.error(f"Error getting coin info: {str(e)}")
            return None 