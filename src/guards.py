"""Giskard Guards API integration for runtime protection."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GUARDS_URL = "https://api.guards.giskard.cloud/guards/v1/chat"


def get_headers() -> dict:
    """Get API headers with authentication."""
    api_key = os.environ.get("GISKARD_GUARDS_API_KEY")
    if not api_key:
        raise ValueError("GISKARD_GUARDS_API_KEY environment variable not set")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }


def screen_input(user_message: str, policy_handle: str = "techcorp-input") -> dict:
    """Screen user input against the input policy.

    Returns dict with 'blocked' (bool), 'action', and detector results.
    """
    response = requests.post(
        GUARDS_URL,
        headers=get_headers(),
        json={
            "messages": [{"role": "user", "content": user_message}],
            "policy_handle": policy_handle,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def screen_output(
    user_message: str,
    assistant_response: str,
    context: list[str] = None,
    policy_handle: str = "techcorp-output",
) -> dict:
    """Screen LLM output for groundedness and policy compliance.

    Returns dict with 'blocked' (bool), 'action', and detector results.
    """
    payload = {
        "messages": [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_response},
        ],
        "policy_handle": policy_handle,
    }
    if context:
        payload["metadata"] = {"context": context}

    response = requests.post(
        GUARDS_URL,
        headers=get_headers(),
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
