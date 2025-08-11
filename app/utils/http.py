
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class HttpClientFactory:
    @staticmethod
    def client(timeout_s: float) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=timeout_s,
            headers={"User-Agent": "local-reco/1.0"},
            follow_redirects=True,
        )

retry_strategy = dict(
    reraise=True,
    retry=retry_if_exception_type((httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.4, min=0.4, max=2.0),
)
