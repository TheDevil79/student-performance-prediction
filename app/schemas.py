"""
Pydantic Schemas for Student Performance Prediction API
Defines validation rules, types, ranges, and documentation for all 30 student attributes.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class StudentFeatures(BaseModel):
    # School & Demographic Features
    school: Literal["GP", "MS"] = Field(
        ...,
        description="Student's school: 'GP' (Gabriel Pereira) or 'MS' (Mousinho da Silveira)",
        examples=["GP"],
    )
    sex: Literal["F", "M"] = Field(
        ...,
        description="Student's sex: 'F' (female) or 'M' (male)",
        examples=["F"],
    )
    age: int = Field(
        ...,
        ge=15,
        le=22,
        description="Student's age (numeric: from 15 to 22)",
        examples=[17],
    )
    address: Literal["U", "R"] = Field(
        ...,
        description="Student's home address type: 'U' (urban) or 'R' (rural)",
        examples=["U"],
    )
    famsize: Literal["LE3", "GT3"] = Field(
        ...,
        description="Family size: 'LE3' (less than or equal to 3) or 'GT3' (greater than 3)",
        examples=["GT3"],
    )
    Pstatus: Literal["T", "A"] = Field(
        ...,
        description="Parent's cohabitation status: 'T' (living together) or 'A' (apart)",
        examples=["T"],
    )

    # Parental Education & Background
    Medu: int = Field(
        ...,
        ge=0,
        le=4,
        description="Mother's education level: 0 (none), 1 (primary 4th grade), 2 (5th-9th grade), 3 (secondary), 4 (higher)",
        examples=[3],
    )
    Fedu: int = Field(
        ...,
        ge=0,
        le=4,
        description="Father's education level: 0 (none), 1 (primary 4th grade), 2 (5th-9th grade), 3 (secondary), 4 (higher)",
        examples=[3],
    )
    Mjob: Literal["teacher", "health", "services", "at_home", "other"] = Field(
        ...,
        description="Mother's job: 'teacher', 'health' care, civil 'services', 'at_home', or 'other'",
        examples=["services"],
    )
    Fjob: Literal["teacher", "health", "services", "at_home", "other"] = Field(
        ...,
        description="Father's job: 'teacher', 'health' care, civil 'services', 'at_home', or 'other'",
        examples=["other"],
    )
    reason: Literal["home", "reputation", "course", "other"] = Field(
        ...,
        description="Reason to choose this school: 'home' (close to home), 'reputation', 'course' preference, or 'other'",
        examples=["reputation"],
    )
    guardian: Literal["mother", "father", "other"] = Field(
        ...,
        description="Student's primary guardian: 'mother', 'father', or 'other'",
        examples=["mother"],
    )

    # Academic & Study Habits
    traveltime: int = Field(
        ...,
        ge=1,
        le=4,
        description="Home to school travel time: 1 (<15 min), 2 (15-30 min), 3 (30 min-1 hour), 4 (>1 hour)",
        examples=[1],
    )
    studytime: int = Field(
        ...,
        ge=1,
        le=4,
        description="Weekly study time: 1 (<2 hours), 2 (2-5 hours), 3 (5-10 hours), 4 (>10 hours)",
        examples=[3],
    )
    failures: int = Field(
        ...,
        ge=0,
        le=4,
        description="Number of past class failures: 0 to 4 (in UCI dataset, 4 represents 3 or more)",
        examples=[0],
    )

    # Educational Support & Activities
    schoolsup: Literal["yes", "no"] = Field(
        ...,
        description="Extra educational school support: 'yes' or 'no'",
        examples=["no"],
    )
    famsup: Literal["yes", "no"] = Field(
        ...,
        description="Family educational support: 'yes' or 'no'",
        examples=["yes"],
    )
    paid: Literal["yes", "no"] = Field(
        ...,
        description="Extra paid classes within the course subject (math): 'yes' or 'no'",
        examples=["no"],
    )
    activities: Literal["yes", "no"] = Field(
        ...,
        description="Extra-curricular activities: 'yes' or 'no'",
        examples=["yes"],
    )
    nursery: Literal["yes", "no"] = Field(
        ...,
        description="Attended nursery school: 'yes' or 'no'",
        examples=["yes"],
    )
    higher: Literal["yes", "no"] = Field(
        ...,
        description="Wants to take higher education: 'yes' or 'no'",
        examples=["yes"],
    )
    internet: Literal["yes", "no"] = Field(
        ...,
        description="Internet access at home: 'yes' or 'no'",
        examples=["yes"],
    )
    romantic: Literal["yes", "no"] = Field(
        ...,
        description="In a romantic relationship: 'yes' or 'no'",
        examples=["no"],
    )

    # Social, Lifestyle & Health Attributes
    famrel: int = Field(
        ...,
        ge=1,
        le=5,
        description="Quality of family relationships: 1 (very bad) to 5 (excellent)",
        examples=[4],
    )
    freetime: int = Field(
        ...,
        ge=1,
        le=5,
        description="Free time after school: 1 (very low) to 5 (very high)",
        examples=[3],
    )
    goout: int = Field(
        ...,
        ge=1,
        le=5,
        description="Going out with friends: 1 (very low) to 5 (very high)",
        examples=[2],
    )
    Dalc: int = Field(
        ...,
        ge=1,
        le=5,
        description="Workday alcohol consumption: 1 (very low) to 5 (very high)",
        examples=[1],
    )
    Walc: int = Field(
        ...,
        ge=1,
        le=5,
        description="Weekend alcohol consumption: 1 (very low) to 5 (very high)",
        examples=[1],
    )
    health: int = Field(
        ...,
        ge=1,
        le=5,
        description="Current health status: 1 (very bad) to 5 (very good)",
        examples=[5],
    )
    absences: int = Field(
        ...,
        ge=0,
        le=93,
        description="Number of school absences (numeric: from 0 to 93)",
        examples=[2],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "school": "GP",
                "sex": "F",
                "age": 17,
                "address": "U",
                "famsize": "GT3",
                "Pstatus": "T",
                "Medu": 4,
                "Fedu": 4,
                "Mjob": "health",
                "Fjob": "teacher",
                "reason": "reputation",
                "guardian": "mother",
                "traveltime": 1,
                "studytime": 3,
                "failures": 0,
                "schoolsup": "no",
                "famsup": "yes",
                "paid": "yes",
                "activities": "yes",
                "nursery": "yes",
                "higher": "yes",
                "internet": "yes",
                "romantic": "no",
                "famrel": 5,
                "freetime": 3,
                "goout": 2,
                "Dalc": 1,
                "Walc": 1,
                "health": 5,
                "absences": 2,
            }
        }
    }


class PredictionResponse(BaseModel):
    predicted_grade: float = Field(
        ...,
        description="Continuous model prediction on a 0–20 scale (clamped to [0.0, 20.0])",
        examples=[14.28],
    )
    rounded_grade: int = Field(
        ...,
        description="Nearest integer grade on the 0–20 scale",
        examples=[14],
    )
    performance_level: str = Field(
        ...,
        description="Qualitative performance tier",
        examples=["Good (14–15)"],
    )
    scale_min: float = 0.0
    scale_max: float = 20.0
    status: str = "success"


class HealthResponse(BaseModel):
    status: str = Field(..., description="'healthy' or 'degraded'")
    model_loaded: bool = Field(..., description="Whether the ML pipeline is loaded in memory")
    model_path: str = Field(..., description="Path to model file")
    version: str = "1.0.0"
    message: Optional[str] = None
