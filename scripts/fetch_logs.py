import sys
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def fetch_logs(url: str) -> str:
    """
    Fetches build logs from GitHub Actions results endpoint with retry logic
    and extended timeouts to prevent HTTPSConnectionPool read timeouts.
    """
    session = requests.Session()
    
    # Configure retry strategy for network instability and server throttling
    retries = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        # Increase read timeout from 20s to 120s (connect_timeout=10s, read_timeout=120s)
        response = session.get(url, timeout=(10, 120))
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Log fetch error: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        log_url = sys.argv[1]
        print(fetch_logs(log_url))
    else:
        print("Usage: python fetch_logs.py <LOG_URL>", file=sys.stderr)
        sys.exit(1)
