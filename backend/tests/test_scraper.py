import unittest
import sys
import os

# Add parent directory to path so we can import modules from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import KandilliScraper

class TestKandilliScraper(unittest.TestCase):
    
    def test_parse_data_empty(self):
        result = KandilliScraper.parse_data("")
        self.assertEqual(result, [])

    def test_parse_data_valid(self):
        # A snippet from Kandilli format
        sample_html = """
        <pre>
2024.12.30 14:15:32  38.7410   37.5255        5.0      -.-  1.6  -.-   HEKIMHAN (MALATYA)                                İlksel
2024.12.30 14:10:00  38.7400   37.5200        5.0      -.-  5.2  -.-   HEKIMHAN (MALATYA)                                İlksel
        </pre>
        """
        result = KandilliScraper.parse_data(sample_html)
        self.assertTrue(len(result) >= 1)
        item = result[0]
        self.assertIn("date", item)
        self.assertIn("time", item)
        self.assertIn("mag", item)
        self.assertIsInstance(item['mag'], float)

if __name__ == '__main__':
    unittest.main()
