"""
This schema is sent to the model as JSON schema (via model_json_schema()),
so the field descriptions double as instructions.
Pydantic also enforces the constraints here invalid model output raises ValidationError,
which generate.py feeds back for a retry.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class ChangeType(str, Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    CHORE = "chore"


class PRDescription(BaseModel):
    title: str = Field(
        max_length=72,
        description="Imperative-mood PR title, e.g. 'Fix off-by-one error in pagination'. No trailing period.",
    )
    change_type: ChangeType = Field(
        description="Single best category for the dominant change in this diff."
    )
    summary: str = Field(
        min_length=20,
        description="One or two sentences describing what the diff does. Only what the diff shows; do not speculate about intent.",
    )
    changes: list[str] = Field(
        min_length=1,
        max_length=10,
        description="Bullet list of concrete changes, most important first. One change per item.",
    )
    breaking_change: bool = Field(
        description="True only if the diff shows a change that could break existing consumers (removed/renamed public API, changed behavior)."
    )
    breaking_change_details: Optional[str] = Field(
        default=None,
        description="Required when breaking_change is true: what breaks and for whom. Must be null otherwise.",
    )
    risk_areas: list[str] = Field(
        default_factory=list,
        description="Parts of the codebase this diff touches that are risky or easy to break. Empty list if none stand out.",
    )
    testing_notes: str = Field(
        description="What testing is visible in the diff (changed/added tests). Say 'No tests are included in this diff.' if none appear. Never invent tests.",
    )

    @field_validator("title")
    @classmethod
    def no_trailing_period(cls, v: str) -> str:
        if v.rstrip().endswith("."):
            raise ValueError("title must not end with a period")
        return v

    @model_validator(mode="after")
    def breaking_change_needs_details(self):
        if self.breaking_change and not self.breaking_change_details:
            raise ValueError("breaking_change_details is required when breaking_change is true")
        if not self.breaking_change and self.breaking_change_details:
            raise ValueError("breaking_change_details must be null when breaking_change is false")
        return self