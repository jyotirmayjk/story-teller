from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class SarvamLLMService:
    def __init__(self) -> None:
        self.url = "https://api.sarvam.ai/v1/chat/completions"

    @staticmethod
    def _extract_message_text(content: Any) -> str:
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts: List[str] = []
            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                    continue
                if not isinstance(item, dict):
                    continue
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                    continue
                if item.get("type") == "text" and isinstance(item.get("content"), str):
                    parts.append(item["content"])
            return "".join(parts).strip()
        return ""

    async def stream_completion(self, *, messages: List[Dict]) -> AsyncIterator[str]:
        if not settings.SARVAM_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SARVAM_API_KEY is not configured",
            )

        payload = {
            "model": settings.SARVAM_CHAT_MODEL,
            "messages": messages,
            "temperature": settings.SARVAM_LLM_TEMPERATURE,
            "top_p": 1,
        }
        if settings.SARVAM_LLM_REASONING_EFFORT:
            payload["reasoning_effort"] = settings.SARVAM_LLM_REASONING_EFFORT

        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {settings.SARVAM_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Sarvam chat failed: {response.text}",
                )

            try:
                body = response.json()
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Sarvam chat returned non-JSON response: {response.text}",
                ) from exc

            choices = body.get("choices", [])
            message_content = ""
            if choices:
                message = choices[0].get("message", {}) or {}
                message_content = self._extract_message_text(message.get("content"))

            if message_content:
                yield message_content


sarvam_llm_service = SarvamLLMService()
