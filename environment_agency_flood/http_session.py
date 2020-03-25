"""Flood Session"""

import requests
import urllib.parse
import logging

LOGGER = logging.getLogger(__name__)

class FloodSession(requests.Session):
    """
    Environment Agency real-time flood monitoring API HTTP session

    https://environment.data.gov.uk/flood-monitoring/doc/reference
    """

    def _call(self, base_url, endpoint, **kwargs) -> requests.Response:
        """Base request"""

        # Build URL
        url = urllib.parse.urljoin(base_url, endpoint)

        response = self.get(url, **kwargs)

        # HTTP errors
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            LOGGER.error(e)
            LOGGER.error(e.response.text)
            raise

        return response

    def call(self, base_url: str, endpoint: str, **kwargs) -> dict:
        """Call JSON endpoint"""

        response = self._call(base_url, endpoint, **kwargs)

        data = response.json()

        for meta, value in data['meta'].items():
            LOGGER.debug("META %s: %s", meta, value)

        return data

    def call_iter(self, base_url: str, endpoint: str, **kwargs) -> iter:
        """Generate lines of data"""

        response = self._call(base_url, endpoint, stream=True, **kwargs)

        yield from response.iter_lines(decode_unicode=True)

