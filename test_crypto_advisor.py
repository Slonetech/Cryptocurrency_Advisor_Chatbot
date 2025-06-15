import unittest
from crypto_advisor import CryptoAdvisor, TrendType, MarketCap, EnergyUse, CryptoMetrics

class TestCryptoAdvisor(unittest.TestCase):
    def setUp(self):
        self.advisor = CryptoAdvisor()

    def test_get_trending_cryptos(self):
        trending = self.advisor.get_trending_cryptos()
        self.assertIsInstance(trending, list)
        for crypto in trending:
            self.assertIn(crypto, self.advisor.crypto_db)
            self.assertEqual(
                self.advisor.crypto_db[crypto].price_trend,
                TrendType.RISING
            )

    def test_get_sustainable_cryptos(self):
        sustainable = self.advisor.get_sustainable_cryptos(min_score=7.0)
        self.assertIsInstance(sustainable, list)
        for crypto in sustainable:
            self.assertIn(crypto, self.advisor.crypto_db)
            self.assertGreaterEqual(
                self.advisor.crypto_db[crypto].sustainability_score,
                7.0
            )

    def test_get_best_growth_potential(self):
        best_crypto = self.advisor.get_best_growth_potential()
        self.assertIsNotNone(best_crypto)
        self.assertIn(best_crypto, self.advisor.crypto_db)

    def test_process_query_trending(self):
        response = self.advisor.process_query("What's trending?")
        self.assertIn("Currently trending cryptocurrencies", response)

    def test_process_query_sustainable(self):
        response = self.advisor.process_query("Show me sustainable options")
        self.assertTrue(
            "Most sustainable cryptocurrencies" in response or 
            "No cryptocurrencies currently meet our sustainability criteria" in response
        )

    def test_process_query_growth(self):
        response = self.advisor.process_query("What should I invest in?")
        self.assertIn("shows the best growth potential", response)

    def test_process_query_unknown(self):
        response = self.advisor.process_query("xyz123")
        self.assertIn("I can help you with", response)

if __name__ == '__main__':
    unittest.main() 