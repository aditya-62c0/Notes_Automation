import json
import os
import re
from typing import Any

import requests
from dotenv import load_dotenv

from utils.logger import get_logger


load_dotenv()

log = get_logger(__name__)


class MCPClient:
    """Small OpenAI-compatible LLM client for MCP helper modules.

    Configure with environment variables:
    - OPENAI_API_KEY or MCP_LLM_API_KEY
    - MCP_LLM_API_URL, optional
    - MCP_LLM_MODEL, optional
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("MCP_LLM_API_KEY")
        self.api_url = os.getenv(
            "MCP_LLM_API_URL",
            "https://api.openai.com/v1/chat/completions",
        )
        self.model = os.getenv("MCP_LLM_MODEL", "gpt-4o-mini")
        self.timeout = int(os.getenv("MCP_LLM_TIMEOUT", "30"))

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def ask_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        if not self.is_enabled():
            log.info("MCP LLM API key not found. Using local fallback.")
            return None

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return self._parse_json(content)
        except Exception as exc:
            log.warning(f"MCP LLM request failed. Using local fallback. Error: {exc}")
            return None

    def _parse_json(self, content: str) -> dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))
