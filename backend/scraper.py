"""
Scraper module for fetching and parsing data from the Kandilli Observatory.
"""
import hashlib
import requests
from bs4 import BeautifulSoup

class KandilliScraper:
    """
    Handles fetching and parsing earthquake data from the Kandilli Observatory website.
    Also provides utilities for checking content updates.
    """

    BASE_URL = "http://www.koeri.boun.edu.tr/scripts/lst2.asp"
    _last_hash = None

    @classmethod
    def fetch_data(cls):
        """
        Fetches the raw HTML content from the Kandilli website.
        """
        try:
            response = requests.get(cls.BASE_URL, timeout=30)
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    @classmethod
    def has_updates(cls):
        """
        Checks if the remote content has changed by hashing the <pre> tag content.
        Returns True if changed, False otherwise.
        """
        try:
            response = requests.get(cls.BASE_URL, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            pre = soup.find('pre')

            if pre is None:
                return False

            content = pre.text.strip()
            cur_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

            if cls._last_hash != cur_hash:
                cls._last_hash = cur_hash
                return True
            return False

        except Exception as e: # pylint: disable=broad-exception-caught
            print(f"Update check error: {e}")
            return False

    @staticmethod
    def parse_data(html_content):
        """
        Parses the raw HTML and extracts earthquake information.
        Returns a list of dictionaries.
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, "html.parser")
        pre_tag = soup.find("pre")

        if not pre_tag:
            return []

        raw_data = pre_tag.text
        lines = raw_data.split('\n')
        parsed_earthquakes = []

        for line in lines:
            if len(line) > 100 and line[0].isdigit():
                try:
                    date_val = line[0:10].strip()
                    time_val = line[11:19].strip()
                    lat_val = float(line[21:28].strip())
                    lng_val = float(line[30:37].strip())
                    depth_val = float(line[43:49].strip())
                    mag_val = float(line[60:63].strip())
                    location_val = line[71:121].strip()

                    parsed_earthquakes.append({
                        "date": date_val,
                        "time": time_val,
                        "lat": lat_val,
                        "lng": lng_val,
                        "depth": depth_val,
                        "mag": mag_val,
                        "location": location_val
                    })
                except ValueError:
                    continue

        return parsed_earthquakes
