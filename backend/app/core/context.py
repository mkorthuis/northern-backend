from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserContext:
    user_id: UUID
    is_superuser: bool
    