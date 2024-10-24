from typing import Any

import requests

from regular_execution import CLIENT_ID, CLIENT_SECRET


class TwitchAPI:
    base_url = "https://api.twitch.tv/helix/"

    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.access_token = self._get_access_token()

    def _get_access_token(self) -> str:
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()["access_token"]

    def _get_headers(self):
        return {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

    def _get_response(self, url: str, query_params: dict[str, Any] | None) -> list[dict[str, Any]] | None:
        response = requests.get(url, headers=self._get_headers(), params=query_params, timeout=10)
        response.raise_for_status()
        return response.json().get("data")

    def get_broadcaster_id(self, name: str) -> str | None:
        url = self.base_url + "users"
        query_params = {"login": name}
        data = self._get_response(url, query_params)
        if not data:
            return None
        return data[0].get("id")

    def _get_stream_data(self, stream_data: list[dict[str, Any]]):
        return stream_data[0].get("user_name"), stream_data[0].get("title")

    def get_stream_by_id(self, user_id: str) -> tuple[str | None, str | None]:
        url = self.base_url + "streams"
        query_params = {"user_id": user_id}
        stream_data = self._get_response(url, query_params)
        if not stream_data:
            return None, None
        return self._get_stream_data(stream_data)

    def get_stream_by_name(self, user_name: str) -> tuple[str | None, str | None]:
        url = self.base_url + "streams"
        query_params = {"user_login": user_name}
        stream_data = self._get_response(url, query_params)
        if not stream_data:
            return None, None
        return self._get_stream_data(stream_data)
