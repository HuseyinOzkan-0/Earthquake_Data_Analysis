"""
Unit tests for the analysis module.
"""
import unittest
import sys
import os
import pandas as pd

# pylint: disable=wrong-import-position
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis import SeismologicalAnalyzer
# pylint: enable=wrong-import-position

class TestSeismologicalAnalyzer(unittest.TestCase):
    """Test cases for SeismologicalAnalyzer class."""

    def test_detect_anomalies_empty(self):
        """Test detection with empty dataframe."""
        df = pd.DataFrame()
        result = SeismologicalAnalyzer.detect_anomalies(df)
        self.assertTrue(result.empty)

    def test_detect_anomalies_data(self):
        """Test detection with dummy data containing an outlier."""
        data = {
            'lat': [39.0, 39.1, 39.2] * 20,
            'lng': [35.0, 35.1, 35.2] * 20,
            'depth': [10.0, 10.0, 10.0] * 20,
            'mag': [2.0, 2.1, 2.2] * 20
        }
        df = pd.DataFrame(data)
        outlier = pd.DataFrame({
            'lat': [39.0], 'lng': [35.0], 'depth': [5.0], 'mag': [9.5]
        })
        df = pd.concat([df, outlier], ignore_index=True)

        result = SeismologicalAnalyzer.detect_anomalies(df)
        self.assertIn('is_anomaly', result.columns)

        self.assertTrue(result['is_anomaly'].dtype == bool)

    def test_predict_next_events_empty(self):
        """Test prediction with empty dataframe."""
        df = pd.DataFrame()
        result = SeismologicalAnalyzer.predict_next_events(df)
        self.assertEqual(result, [])

    def test_predict_next_events_basic(self):
        """Test prediction with basic data."""
        data = {
            'location': ['LOC_A', 'LOC_A', 'LOC_B'],
            'mag': [3.0, 4.0, 2.0],
            'date': ['2023-01-01', '2023-01-02', '2023-01-03']
        }
        df = pd.DataFrame(data)
        result = SeismologicalAnalyzer.predict_next_events(df)
        self.assertTrue(isinstance(result, list))
        if len(result) > 0:
            self.assertIn('risk_score', result[0])

if __name__ == '__main__':
    unittest.main()
