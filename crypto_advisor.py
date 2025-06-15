import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, timedelta
import re
import os
import openai
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendType(Enum):
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"

class MarketCap(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class EnergyUse(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class CryptoMetrics:
    price_trend: TrendType
    market_cap: MarketCap
    energy_use: EnergyUse
    sustainability_score: float
    risk_level: RiskLevel
    last_updated: datetime
    price_change_24h: float  # Percentage change in last 24 hours
    volume_24h: float  # Trading volume in USD
    market_dominance: float  # Percentage of total crypto market cap

class CryptoAdvisor:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OpenAI API key not found. Some features may be limited.")
        else:
            openai.api_key = self.api_key
        
        self.system_prompt = """You are a cryptocurrency advisor AI assistant. Your role is to:
1. Provide accurate and helpful information about cryptocurrencies
2. Analyze market trends and patterns
3. Offer investment advice while maintaining appropriate disclaimers
4. Explain technical concepts in simple terms
5. Stay up-to-date with the latest crypto developments
6. Consider sustainability and environmental impact
7. Assess risks and potential returns
8. Provide balanced and objective analysis

Remember to:
- Always include appropriate disclaimers about investment risks
- Be clear about the speculative nature of cryptocurrencies
- Consider both technical and fundamental analysis
- Acknowledge market volatility
- Suggest diversification strategies
- Consider regulatory aspects
- Be transparent about limitations
- Maintain professional and ethical standards"""

        self.crypto_db = {
            "Bitcoin": CryptoMetrics(
                price_trend=TrendType.RISING,
                market_cap=MarketCap.HIGH,
                energy_use=EnergyUse.HIGH,
                sustainability_score=3.0/10.0,
                risk_level=RiskLevel.MEDIUM,
                last_updated=datetime.now(),
                price_change_24h=2.5,
                volume_24h=25000000000.0,
                market_dominance=45.0
            ),
            "Ethereum": CryptoMetrics(
                price_trend=TrendType.STABLE,
                market_cap=MarketCap.HIGH,
                energy_use=EnergyUse.MEDIUM,
                sustainability_score=6.0/10.0,
                risk_level=RiskLevel.MEDIUM,
                last_updated=datetime.now(),
                price_change_24h=1.2,
                volume_24h=15000000000.0,
                market_dominance=20.0
            ),
            "Cardano": CryptoMetrics(
                price_trend=TrendType.RISING,
                market_cap=MarketCap.MEDIUM,
                energy_use=EnergyUse.LOW,
                sustainability_score=8.0/10.0,
                risk_level=RiskLevel.MEDIUM,
                last_updated=datetime.now(),
                price_change_24h=3.5,
                volume_24h=2000000000.0,
                market_dominance=2.0
            ),
            "Solana": CryptoMetrics(
                price_trend=TrendType.RISING,
                market_cap=MarketCap.MEDIUM,
                energy_use=EnergyUse.LOW,
                sustainability_score=7.5/10.0,
                risk_level=RiskLevel.HIGH,
                last_updated=datetime.now(),
                price_change_24h=4.2,
                volume_24h=1800000000.0,
                market_dominance=1.5
            ),
            "Polkadot": CryptoMetrics(
                price_trend=TrendType.STABLE,
                market_cap=MarketCap.MEDIUM,
                energy_use=EnergyUse.LOW,
                sustainability_score=7.0/10.0,
                risk_level=RiskLevel.HIGH,
                last_updated=datetime.now(),
                price_change_24h=0.8,
                volume_24h=1200000000.0,
                market_dominance=1.0
            ),
            "Avalanche": CryptoMetrics(
                price_trend=TrendType.RISING,
                market_cap=MarketCap.MEDIUM,
                energy_use=EnergyUse.LOW,
                sustainability_score=7.8/10.0,
                risk_level=RiskLevel.HIGH,
                last_updated=datetime.now(),
                price_change_24h=5.5,
                volume_24h=1500000000.0,
                market_dominance=0.8
            )
        }
        self.disclaimer = "⚠️ DISCLAIMER: Cryptocurrency investments are highly volatile and risky. This advice is for educational purposes only. Always do your own research and consult with financial advisors before making investment decisions."
        
        # Add sentiment analysis keywords
        self.sentiment_keywords = {
            'positive': ['bullish', 'growth', 'potential', 'innovation', 'adoption', 'partnership', 'upgrade'],
            'negative': ['bearish', 'risk', 'concern', 'regulation', 'hack', 'vulnerability', 'decline'],
            'neutral': ['stable', 'maintain', 'update', 'announcement', 'development']
        }
        
        # Add investment strategy templates
        self.strategy_templates = {
            'conservative': {
                'description': 'Focus on established cryptocurrencies with high market cap and stability',
                'risk_level': RiskLevel.LOW,
                'time_horizon': 'long-term',
                'recommended_coins': ['Bitcoin', 'Ethereum']
            },
            'moderate': {
                'description': 'Balance between established and emerging cryptocurrencies',
                'risk_level': RiskLevel.MEDIUM,
                'time_horizon': 'medium-term',
                'recommended_coins': ['Cardano', 'Solana', 'Polkadot']
            },
            'aggressive': {
                'description': 'Focus on high-growth potential cryptocurrencies with higher risk',
                'risk_level': RiskLevel.HIGH,
                'time_horizon': 'short-term',
                'recommended_coins': ['Avalanche', 'Solana']
            }
        }

    def get_trending_cryptos(self, min_price_change: float = 0.0) -> List[str]:
        """Returns list of cryptocurrencies with rising price trends and minimum price change."""
        return [
            crypto for crypto, metrics in self.crypto_db.items()
            if metrics.price_trend == TrendType.RISING and metrics.price_change_24h >= min_price_change
        ]

    def get_sustainable_cryptos(self, min_score: float = 7.0) -> List[str]:
        """Returns list of cryptocurrencies with high sustainability scores."""
        return [
            crypto for crypto, metrics in self.crypto_db.items()
            if metrics.sustainability_score >= min_score
        ]

    def get_risk_adjusted_recommendations(self, risk_tolerance: RiskLevel) -> List[str]:
        """Returns cryptocurrencies matching the user's risk tolerance."""
        return [
            crypto for crypto, metrics in self.crypto_db.items()
            if metrics.risk_level == risk_tolerance
        ]

    def get_market_leaders(self, min_dominance: float = 1.0) -> List[str]:
        """Returns cryptocurrencies with significant market dominance."""
        return [
            crypto for crypto, metrics in self.crypto_db.items()
            if metrics.market_dominance >= min_dominance
        ]

    def get_best_growth_potential(self, risk_tolerance: Optional[RiskLevel] = None) -> Optional[str]:
        """Returns the cryptocurrency with the best growth potential based on multiple factors."""
        best_crypto = None
        best_score = -1

        for crypto, metrics in self.crypto_db.items():
            if risk_tolerance and metrics.risk_level != risk_tolerance:
                continue

            score = 0
            # Price trend weight
            if metrics.price_trend == TrendType.RISING:
                score += 3
            elif metrics.price_trend == TrendType.STABLE:
                score += 1

            # Market cap weight
            if metrics.market_cap == MarketCap.HIGH:
                score += 2
            elif metrics.market_cap == MarketCap.MEDIUM:
                score += 1

            # Sustainability weight
            score += metrics.sustainability_score

            # Volume and price change weight
            score += (metrics.price_change_24h / 10) + (metrics.volume_24h / 10000000000)

            if score > best_score:
                best_score = score
                best_crypto = crypto

        return best_crypto

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text using keyword matching."""
        words = text.lower().split()
        sentiment_scores = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for word in words:
            for sentiment, keywords in self.sentiment_keywords.items():
                if word in keywords:
                    sentiment_scores[sentiment] += 1
        
        total = sum(sentiment_scores.values())
        if total > 0:
            return {k: v/total for k, v in sentiment_scores.items()}
        return sentiment_scores

    def get_investment_strategy(self, risk_tolerance: str, investment_amount: float) -> Dict:
        """Generate personalized investment strategy based on risk tolerance and amount."""
        strategy = self.strategy_templates.get(risk_tolerance.lower())
        if not strategy:
            return None
            
        # Calculate allocation based on investment amount
        recommended_coins = strategy['recommended_coins']
        allocation = investment_amount / len(recommended_coins)
        
        return {
            'strategy': strategy['description'],
            'risk_level': strategy['risk_level'].value,
            'time_horizon': strategy['time_horizon'],
            'recommendations': [
                {
                    'coin': coin,
                    'allocation': allocation,
                    'metrics': self.crypto_db[coin]
                }
                for coin in recommended_coins
            ]
        }

    def get_market_insights(self) -> str:
        """Generate AI-powered market insights."""
        rising_count = len(self.get_trending_cryptos())
        total_count = len(self.crypto_db)
        market_health = "bullish" if rising_count > total_count/2 else "bearish"
        
        # Calculate market sentiment
        sustainable_count = len(self.get_sustainable_cryptos())
        sustainability_trend = "improving" if sustainable_count > total_count/2 else "needs attention"
        
        return (
            f"🤖 AI Market Analysis:\n"
            f"• Market Sentiment: {market_health.upper()}\n"
            f"• {rising_count}/{total_count} cryptocurrencies are trending up\n"
            f"• Sustainability Trend: {sustainability_trend}\n"
            f"• Top Performers: {', '.join(self.get_trending_cryptos(min_price_change=3.0))}\n"
            f"• Most Sustainable: {', '.join(self.get_sustainable_cryptos(min_score=7.5))}\n"
            f"• Market Leaders: {', '.join(self.get_market_leaders(5.0))}\n"
        )

    def process_query(self, query: str) -> str:
        """Process a user query and return a response."""
        try:
            # Check if OpenAI API key is set
            if not os.getenv('OPENAI_API_KEY'):
                logger.error("OpenAI API key not found")
                return "I apologize, but I'm currently unable to process your request. Please ensure the OpenAI API key is properly configured."

            # Get market data for context
            market_data = self._get_market_context()
            trending = self.get_trending_cryptos()

            # Prepare the prompt with market context
            prompt = f"""As a cryptocurrency advisor, please provide a helpful response to the following query.
            Use the current market data to inform your response:

            Market Overview:
            - Total Market Cap: {market_data['total_market_cap']:,.2f}
            - 24h Volume: {market_data['total_volume']:,.2f}
            - BTC Dominance: {market_data['btc_dominance']:.2f}%
            - Market Trend: {market_data['market_trend']}

            Trending Coins:
            {', '.join([coin['name'] for coin in trending])}

            User Query: {query}

            Please provide a clear, informative response that:
            1. Directly addresses the user's question
            2. Uses the market data to support your points
            3. Maintains a professional but friendly tone
            4. Includes relevant market insights
            5. Suggests potential next steps or considerations"""

            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a knowledgeable cryptocurrency advisor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "I apologize, but I'm currently unable to process your request. Please try again later."

    def _get_market_context(self) -> str:
        """Get current market context for the AI."""
        try:
            # Get global market data
            response = requests.get('https://api.coingecko.com/api/v3/global')
            data = response.json()
            
            market_data = data.get('data', {})
            total_market_cap = market_data.get('total_market_cap', {}).get('usd', 0)
            total_volume = market_data.get('total_volume', {}).get('usd', 0)
            btc_dominance = market_data.get('market_cap_percentage', {}).get('btc', 0)
            
            # Get top coins
            top_coins_response = requests.get(
                'https://api.coingecko.com/api/v3/coins/markets',
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 5,
                    'page': 1,
                    'sparkline': False
                }
            )
            top_coins = top_coins_response.json()
            
            # Format market context
            context = f"""
            Current Market Overview:
            - Total Market Cap: ${total_market_cap:,.2f}
            - 24h Trading Volume: ${total_volume:,.2f}
            - Bitcoin Dominance: {btc_dominance:.2f}%
            
            Top 5 Cryptocurrencies:
            {self._format_top_coins(top_coins)}
            """
            
            return {
                'total_market_cap': total_market_cap,
                'total_volume': total_volume,
                'btc_dominance': btc_dominance,
                'market_trend': 'bullish' if total_market_cap > 0 else 'bearish',
            }

        except Exception as e:
            logger.error(f"Error getting market context: {str(e)}")
            return {
                "error": "Unable to get market context",
            }

    def _format_top_coins(self, coins: List[Dict]) -> str:
        """Format top coins information."""
        formatted = []
        for coin in coins:
            price_change = coin.get('price_change_percentage_24h', 0)
            formatted.append(
                f"- {coin['name']} (${coin['current_price']:,.2f}): {price_change:+.2f}%"
            )
        return "\n".join(formatted)

    def analyze_market_health(self) -> Dict:
        """Analyze overall market health using AI."""
        try:
            market_context = self._get_market_context()
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Current market context: {market_context}"},
                {"role": "user", "content": "Analyze the current market health and provide a detailed assessment."}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )

            analysis = response.choices[0].message.content

            return {
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "market_context": market_context
            }

        except Exception as e:
            logger.error(f"Error analyzing market health: {str(e)}")
            return {
                "error": "Unable to analyze market health",
                "timestamp": datetime.now().isoformat()
            }

    def generate_investment_strategy(self, risk_profile: str) -> Dict:
        """Generate personalized investment strategy using AI."""
        try:
            market_context = self._get_market_context()
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Current market context: {market_context}"},
                {"role": "user", "content": f"Generate a detailed investment strategy for a {risk_profile} risk profile."}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            strategy = response.choices[0].message.content

            return {
                "strategy": strategy,
                "risk_profile": risk_profile,
                "timestamp": datetime.now().isoformat(),
                "market_context": market_context
            }

        except Exception as e:
            logger.error(f"Error generating investment strategy: {str(e)}")
            return {
                "error": "Unable to generate investment strategy",
                "timestamp": datetime.now().isoformat()
            }

def main():
    advisor = CryptoAdvisor()
    print("🤖 Welcome to Slone_cryptoBuddy! Your AI-powered crypto advisor!")
    print("Type 'exit' to quit.")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'exit':
                print("Goodbye! Remember to always do your own research! 👋")
                break
                
            response = advisor.process_query(user_input)
            print(f"\nSlone_cryptoBuddy: {response}")
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            print("I apologize, but I encountered an error. Please try again.")

if __name__ == "__main__":
    main() 