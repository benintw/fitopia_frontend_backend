"""API utils for frontend"""

import requests
import streamlit as st
from typing import Dict, Optional, List

API_BASE_URL = "http://localhost:8000"


class APIError(Exception):
    pass


def safe_request(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            raise APIError(f"API request failed: {str(e)}")

    return wrapper


@safe_request
def get_members() -> List[Dict]:
    response = requests.get(f"{API_BASE_URL}/members")
    if response.status_code == 200:
        return response.json()
    raise APIError(f"Failed to get members: {response.status_code}")


@safe_request
def create_member(data: Dict) -> bool:
    response = requests.post(f"{API_BASE_URL}/members", json=data)
    return response.status_code == 200



