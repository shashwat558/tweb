from __future__ import annotations

import httpx

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


class NetworkError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)


class NetworkClient:
    def __init__(self, timeout: float = 30.0, max_redirects: int = 10) -> None:
        self._timeout = timeout
        self._max_redirects = max_redirects
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                max_redirects=self._max_redirects,
                headers={"User-Agent": _USER_AGENT},
                verify=True,
            )
        return self._client

    async def fetch(self, url: str) -> httpx.Response:
        try:
            client = await self._get_client()
            response = await client.get(url)
            self._check_status(response)
            return response
        except httpx.TimeoutException:
            raise NetworkError(f"Connection timed out: {url}")
        except httpx.ConnectError as e:
            raise NetworkError(f"Could not connect to {url}: {e}")
        except httpx.DNSLookupError:
            raise NetworkError(f"DNS lookup failed for {url}")
        except httpx.TooManyRedirects:
            raise NetworkError(f"Too many redirects for {url}")
        except httpx.InvalidURL:
            raise NetworkError(f"Invalid URL: {url}")
        except httpx.HTTPError as e:
            raise NetworkError(f"HTTP error: {e}")

    async def submit(self, url: str, method: str, data: dict[str, str]) -> httpx.Response:
        try:
            client = await self._get_client()
            if method.upper() == "GET":
                response = await client.get(url, params=data)
            else:
                response = await client.post(url, data=data)
            self._check_status(response)
            return response
        except httpx.TimeoutException:
            raise NetworkError(f"Connection timed out: {url}")
        except httpx.ConnectError as e:
            raise NetworkError(f"Could not connect to {url}: {e}")
        except httpx.DNSLookupError:
            raise NetworkError(f"DNS lookup failed for {url}")
        except httpx.TooManyRedirects:
            raise NetworkError(f"Too many redirects for {url}")
        except httpx.InvalidURL:
            raise NetworkError(f"Invalid URL: {url}")
        except httpx.HTTPError as e:
            raise NetworkError(f"HTTP error: {e}")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _check_status(self, response: httpx.Response) -> None:
        status = response.status_code
        url = str(response.url)
        if status == 404:
            raise NetworkError(f"Page not found (404): {url}", 404)
        if status == 403:
            raise NetworkError(f"Access forbidden (403): {url}", 403)
        if status == 429:
            raise NetworkError(f"Rate limited (429): {url}", 429)
        if status >= 500:
            raise NetworkError(f"Server error ({status}): {url}", status)
