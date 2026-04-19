from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings


class RuntimeTraceService:
    @staticmethod
    def append_turn(payload: dict[str, Any]) -> Path:
        output_path = Path(settings.RUNTIME_TRACE_JSONL)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
        return output_path


runtime_trace_service = RuntimeTraceService()
