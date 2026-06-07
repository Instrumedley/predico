"""
Pydantic schemas for league endpoints.
"""
from datetime import datetime
from typing import List, Optional

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


class JoinLeagueRequest(BaseModel):
    invite_code: Optional[str] = Field(None, max_length=50)


class LeagueInviteRequest(BaseModel):
    emails: List[str] = Field(..., min_length=1, max_length=20)


class LeagueInviteResponse(BaseModel):
    sent: List[str]
    failed: List[str]


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


class LeagueMemberRanking(BaseModel):
    rank: int
    user_id: int
    username: str
    total_points: int


class LeagueDetail(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_private: bool
    created_at: datetime
    created_by: int
    member_count: int
    is_member: bool
    is_creator: bool
    rankings: List[LeagueMemberRanking] = []


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
