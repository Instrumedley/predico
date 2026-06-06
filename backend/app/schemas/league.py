"""
Pydantic schemas for league endpoints.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LeagueCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: bool = False
    password: Optional[str] = Field(None, min_length=4, max_length=50)

    @model_validator(mode="after")
    def require_password_for_private(self) -> "LeagueCreate":
        if self.is_private and not self.password:
            raise ValueError("Password is required for private leagues")
        if not self.is_private:
            self.password = None
        return self


class LeagueSummary(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_private: bool
    created_at: datetime
    member_count: int
    is_member: bool = False

    class Config:
        from_attributes = True


class LeagueCreateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_private: bool
    created_at: datetime
    member_count: int
    invite_code: Optional[str] = None

    class Config:
        from_attributes = True
