from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
from uuid import uuid4


@dataclass
class TempAuthStore:
    token_to_household_id: Dict[str, int] = field(default_factory=dict)
    token_to_household_name: Dict[str, str] = field(default_factory=dict)

    def issue_token(self, *, household_id: int, household_name: str) -> str:
        token = f"demo-token-{uuid4().hex[:24]}"
        self.token_to_household_id[token] = household_id
        self.token_to_household_name[token] = household_name
        return token

    def get_household_id(self, token: str) -> Optional[int]:
        return self.token_to_household_id.get(token)

    def is_valid(self, token: str) -> bool:
        return token in self.token_to_household_id


temp_auth_store = TempAuthStore()
