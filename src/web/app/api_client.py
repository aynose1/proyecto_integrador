from __future__ import annotations

import requests
from flask import current_app, session


class APIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class APIClient:
    def __init__(self, token: str | None = None):
        self.base_url = current_app.config["API_BASE_URL"]
        self.token = token

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _handle_response(self, response: requests.Response):
        if response.status_code == 204:
            return None
        if response.ok:
            if response.content:
                return response.json()
            return None
        try:
            payload = response.json()
            detail = payload.get("detail", response.text)
            if isinstance(detail, list):
                detail = "; ".join(str(item) for item in detail)
        except ValueError:
            detail = response.text or "Error desconocido en la API"
        raise APIError(str(detail), response.status_code)

    def get(self, path: str, params: dict | None = None):
        response = requests.get(self._url(path), headers=self._headers(), params=params, timeout=30)
        return self._handle_response(response)

    def post(self, path: str, data: dict | None = None):
        response = requests.post(self._url(path), headers=self._headers(), json=data, timeout=30)
        return self._handle_response(response)

    def put(self, path: str, data: dict | None = None):
        response = requests.put(self._url(path), headers=self._headers(), json=data, timeout=30)
        return self._handle_response(response)

    def patch(self, path: str, data: dict | None = None):
        response = requests.patch(self._url(path), headers=self._headers(), json=data, timeout=30)
        return self._handle_response(response)

    def delete(self, path: str):
        response = requests.delete(self._url(path), headers=self._headers(), timeout=30)
        return self._handle_response(response)

    def login(self, codigo_usuario: str, contrasena: str) -> dict:
        return self.post("/auth/login", {"codigo_usuario": codigo_usuario, "contrasena": contrasena})

    def refresh(self, refresh_token: str) -> dict:
        return self.post("/auth/refresh", {"refresh_token": refresh_token})


def get_api_client() -> APIClient:
    return APIClient(token=session.get("access_token"))

def api_request(method: str, path: str, **kwargs):
    client = get_api_client()

    try:
        return getattr(client, method)(path, **kwargs)
    except APIError as exc:
        if exc.status_code == 401 and session.get("refresh_token"):
            tokens = client.refresh(session["refresh_token"])
            session["access_token"] = tokens["access_token"]
            session["refresh_token"] = tokens["refresh_token"]
            client = APIClient(token=session["access_token"])
            return getattr(client, method)(path, **kwargs)
        raise
