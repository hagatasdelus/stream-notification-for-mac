# -*- coding: utf-8 -*-

"""
This module provides an asynchronous client for interacting with the Twitch API.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from src import CLIENT_ID, CLIENT_SECRET
from src.constants import AppConstant

logger = logging.getLogger(__name__)

class TwitchAPIError(Exception):
    """Exception raised for errors in the Twitch API client.
    """

class TwitchAPI:
    """Asynchronous client for interacting with the Twitch API.

    Attributes:
        base_url (str): The base URL for the Twitch API.
        timeout (ClientTimeout): The timeout settings for the client.
        client_id (str): The client ID for the Twitch API.
        client_secret (str): The client secret for the Twitch API.
        session (ClientSession): The client session for making requests.
        access_token (str): The access token for the Twitch API.
        _token_lock (asyncio.Lock): A lock for ensuring access token is retrieved or updated safely.
    """

    base_url = "https://api.twitch.tv/helix/"
    timeout = ClientTimeout(total=AppConstant.TIMEOUT_SECONDS)

    def __init__(self):
        """Initialize the API client.

        Attributes:
            client_id (str): The client ID for the Twitch API.
            client_secret (str): The client secret for the Twitch API.
            session (ClientSession): The client session for making requests.
            access_token (str): The access token for the Twitch API.
            _token_lock (asyncio.Lock): A lock for ensuring access token is retrieved or updated safely.
        """
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.session: ClientSession | None = None
        self.access_token: str | None = None
        self._token_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Initialize the API client."""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
            await self._ensure_access_token()

    async def close(self) -> None:
        """Close the API client.
        """
        if self.session:
            await self.session.close()
            self.session = None
            self.access_token = None

    async def _ensure_access_token(self) -> None:
        """Ensure that the access token is available.
        """
        async with self._token_lock:  # 並行処理での競合を防ぐ
            if not self.access_token:
                await self._get_access_token()

    async def _get_access_token(self) -> None:
        """Get the access token for the Twitch API.
        """
        if not self.session:
            raise TwitchAPIError(
                AppConstant.ERROR_SESSION_NOT_INITIALIZED
            )

        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": AppConstant.GRANT_TYPE,
        }

        try:
            async with self.session.post(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                self.access_token = data["access_token"]
        except aiohttp.ClientError as e:
            logger.exception(AppConstant.ERROR_ACCESS_TOKEN_FAILED)
            error_msg = f"{AppConstant.ERROR_ACCESS_TOKEN_FAILED}: {str(e)}"
            raise TwitchAPIError(error_msg) from e

    def _get_headers(self) -> dict[str, str]:
        """Get the headers for the API request.
        """
        if not self.access_token:
            raise TwitchAPIError(
                AppConstant.ERROR_ACCESS_TOKEN_NOT_AVAILABLE
            )

        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

    @asynccontextmanager
    async def _make_request(self, url: str, query_params: dict[str, Any] | None = None):
        """Make an API request and yield the response.
        """
        if not self.session:
            raise TwitchAPIError(
                AppConstant.ERROR_SESSION_NOT_INITIALIZED
            )

        await self._ensure_access_token()

        try:
            async with self.session.get(
                url,
                headers=self._get_headers(),
                params=query_params
            ) as response:
                yield response
        except aiohttp.ClientError as e:
            logger.exception(AppConstant.ERROR_API_REQUEST_FAILED)
            error_msg = f"{AppConstant.ERROR_API_REQUEST_FAILED}: {str(e)}"
            raise TwitchAPIError(error_msg) from e

    async def _get_response(
        self,
        url: str,
        query_params: Dict[str, Any] | None = None
    ) -> List[Dict[str, Any]] | None:
        """Get the response data from the API.
        
        Args:
            url (str): The URL to make the request to
            query_params (Dict[str, Any] | None, optional): The query parameters. Defaults to None.
            
        Returns:
            List[Dict[str, Any]] | None: The response data if successful, None otherwise
            
        Raises:
            TwitchAPIError: If the request fails
        """
        async with self._make_request(url, query_params) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("data")

    async def get_broadcaster(self, name: str) -> dict | None:
        """Get the broadcaster information.
        
        Args:
            name (str): The username of the broadcaster
        
        Returns:
            Optional[BroadcasterData]: The broadcaster information if found, None otherwise
        """
        url = self.base_url + "users"
        query_params = {"login": name}
        try:
            data = await self._get_response(url, query_params)
            if not data or not data[0]:
                return None

            return data[0]
        except (TwitchAPIError, IndexError):
            logger.exception("Failed to get broadcaster info for %s", name)
            return None

    async def get_stream_by_id(
        self,
        user_id: str
    ) -> tuple[str | None, str | None]:
        """Get the stream data for a given user ID."""
        url = self.base_url + "streams"
        query_params = {"user_id": user_id}

        try:
            stream_data = await self._get_response(url, query_params)
            if not stream_data:
                return None, None
            return self._get_stream_data(stream_data)
        except TwitchAPIError:
            logger.exception("Failed to get stream data for user ID %s", user_id)
            return None, None

    async def get_stream_by_name(
        self,
        user_name: str
    ) -> tuple[str | None, str | None]:
        """Get the stream data for a given user name.
        """
        url = self.base_url + "streams"
        query_params = {"user_login": user_name}

        try:
            stream_data = await self._get_response(url, query_params)
            if not stream_data:
                return None, None
            return self._get_stream_data(stream_data)
        except TwitchAPIError:
            logger.exception("Failed to get stream data for user %s", user_name)
            return None, None

    def _get_stream_data(
        self,
        stream_data: list[dict[str, Any]]
    ) -> tuple[str | None, str | None]:
        """Get the stream data from the API response."""
        return stream_data[0].get("user_name"), stream_data[0].get("title")
