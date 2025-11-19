"""
Database Schemas

Portfolio data models for MongoDB using Pydantic (v2).
Each Pydantic model corresponds to a collection in MongoDB (lowercased class name).

Collections:
- user
- project
- skill
- testimonial
- certificate
- activitylog
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime


class User(BaseModel):
    email: str = Field(..., description="Unique email for login")
    password_hash: str = Field(..., description="BCrypt hash of password")
    name: Optional[str] = Field(None, description="Display name")
    role: str = Field("admin", description="User role: admin/editor/viewer")
    is_active: bool = Field(True)


class Project(BaseModel):
    title: str
    slug: str
    shortDesc: str = Field(..., description="Short description")
    longDesc: Optional[str] = Field(None, description="Rich text (HTML)")
    tech: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    liveDemoUrl: Optional[str] = None
    githubUrl: Optional[str] = None
    images: List[str] = Field(default_factory=list, description="Image URLs")
    featured: bool = False
    published: bool = False
    orderIndex: int = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    deleted: bool = False


class Skill(BaseModel):
    name: str
    level: int = Field(ge=0, le=100)
    category: str
    icon: Optional[str] = None
    description: Optional[str] = None
    orderIndex: int = 0
    published: bool = True
    deleted: bool = False


class Testimonial(BaseModel):
    name: str
    role: Optional[str] = None
    quote: str
    avatar: Optional[str] = None
    sourceUrl: Optional[str] = None
    orderIndex: int = 0
    published: bool = False
    deleted: bool = False


class Certificate(BaseModel):
    title: str
    issuer: str
    issueDate: str
    image: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    published: bool = False
    deleted: bool = False


class ActivityLog(BaseModel):
    user_email: str
    action: str
    entity: str
    entity_id: str
    metadata: dict = Field(default_factory=dict)
    timestamp: Optional[datetime] = None
