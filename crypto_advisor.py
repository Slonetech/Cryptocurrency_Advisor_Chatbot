# crypto_advisor.py
import os
import json
import requests
from dotenv import load_dotenv
import logging

# Assuming CryptoAPI is defined in crypto_api.py and provides data fetching methods
from crypto_api import CryptoAPI # Import the CryptoAPI class

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class CryptoAdvisor:
    def __init__(self, crypto_api_instance: CryptoAPI = None):
        # Environment variables for API keys and Ollama URL
        self.OLLAMA_API_BASE_URL = os.getenv('OLLAMA_API_BASE_URL', 'http://localhost:11434')
        self.GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') # Assuming you're also using Gemini for some models
        
        # Use the provided CryptoAPI instance, or create a new one if not provided
        self.crypto_api = crypto_api_instance if crypto_api_instance else CryptoAPI()

    # --- Ollama Integration ---
    def _get_ollama_response(self, prompt, model="llama3"):
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(f"{self.OLLAMA_API_BASE_URL}/api/generate", headers=headers, json=data)
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with Ollama: {e}")
            return f"Sorry, I couldn't connect to the AI model. Error: {e}"

    # --- AI Query Processing ---
    def process_query(self, query):
        market_data = self.crypto_api.get_market_data()
        trending = self.crypto_api.get_trending_coins()

        # Ensure trending is a list before proceeding
        if not isinstance(trending, list):
            logger.warning(f"Trending data is not a list, received: {trending}. Defaulting to empty list.")
            trending = [] # Default to an empty list to prevent errors

        # Construct a detailed prompt for the AI model
        prompt_parts = []
        
        if market_data and market_data.get('coins'):
            prompt_parts.append("Current Cryptocurrency Market Data Overview:")
            prompt_parts.append(f"- Total Market Cap: ${market_data.get('total_market_cap', 0):.2f}")
            prompt_parts.append(f"- Total 24h Volume: ${market_data.get('total_volume', 0):.2f}")
            prompt_parts.append(f"- Bitcoin Dominance: {market_data.get('btc_dominance', 0):.2f}%")
            
            # Top 5 coins by market cap
            top_coins = sorted(market_data['coins'], key=lambda x: x.get('market_cap', 0), reverse=True)[:5]
            if top_coins:
                prompt_parts.append("\nTop 5 Cryptocurrencies by Market Cap:")
                for coin in top_coins:
                    prompt_parts.append(f"  - {coin.get('name', 'N/A')} ({coin.get('symbol', 'N/A').upper()}): Current Price ${coin.get('current_price', 0):.2f}, 24h Change {coin.get('price_change_percentage_24h', 0):.2f}%")
            else:
                prompt_parts.append("\nNo top cryptocurrencies available.")
        else:
            prompt_parts.append("No market data available to include in the prompt.")


        if trending: # 'trending' is guaranteed to be a list here due to the check above
            prompt_parts.append("\nCurrently Trending Cryptocurrencies:")
            for trend_coin in trending:
                coin_name = trend_coin.get('name', 'N/A')
                # The trending API response from CoinGecko typically does not include price_change_percentage_24h directly for trending coins.
                # Your crypto_api.py's get_trending_coins also does not add it.
                # If you need it, you'd have to fetch market data for each trending coin, which can be API intensive.
                # For now, I'm removing price_change_percentage_24h from the trending prompt as it's not consistently available in the trending API response directly.
                prompt_parts.append(f"  - {coin_name} ({trend_coin.get('symbol', 'N/A').upper()}) - Rank: {trend_coin.get('market_cap_rank', 'N/A')}")
        else:
            prompt_parts.append("\nNo trending coins available.")

        prompt_parts.append(f"\nUser Query: {query}\n")
        prompt_parts.append("Based on the above information, and your general cryptocurrency knowledge, please provide a concise and helpful response to the user's query.")
        prompt_parts.append("If the user asks for investment advice, provide general insights and suggest consulting a financial advisor. Avoid making direct predictions.")
        prompt_parts.append("If the user asks for market data that is already provided above, simply refer to it or summarize it from the provided data.")


        full_prompt = "\n".join(prompt_parts)
        logger.info(f"Sending prompt to Ollama:\n{full_prompt[:500]}...") # Log truncated prompt
        
        try:
            response = self._get_ollama_response(full_prompt)
            return response
        except Exception as e:
            logger.error(f"Error getting AI response for query: {e}")
            return f"ERROR: Could not get response from AI model: {e}"

# If you had any authentication related functions here, they should be moved to app.py or models.py
# as `crypto_advisor.py` should focus purely on the AI and data processing logic.