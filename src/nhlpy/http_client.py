import httpx
import logging

class HttpClient:
    def __init__(self, _config) -> None:
        self._config = _config
        if self._config.verbose:
            logging.basicConfig(level=logging.INFO)

    def get(self,resource: str) -> httpx.request:
        try:
            r: httpx.request = httpx.get(
                    url=f"{self._config.api_web_base_url}{self._config.api_web_api_ver}{resource}", follow_redirects=True
            )

            if self._config.verbose:
                logging.info(F"API URL: {r.url}")

            return r
        except httpx.ReadTimeout as exc:
            logging.info(f"Time out error as:\n {exc}")
            exit()
            

    def get_by_url(self, full_resource: str) -> httpx.request:
        r: httpx.request = httpx.get(url=full_resource, follow_redirects=True)

        if self._config.verbose:
            logging.info(f"API URL: {r.url}")

        return r

