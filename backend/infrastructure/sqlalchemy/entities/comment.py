from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.domain.entities.user import User
from backend.infrastructure.sqlalchemy.base import Base
from backend.infrastructure.sqlalchemy.mixin import Schema


class CommentSchema(Base, Schema):
    __tablename__ = "comment"

    content: Mapped[str]

    meal_id: Mapped[int] = mapped_column(ForeignKey("meal.id"))
    parent_id: Mapped[int] = mapped_column(ForeignKey("comment.id"))

    replies: Mapped[CommentSchema] = relationship(
        "Comment", backref="parent", lazy="dynamic", remote_side="CommentSchema.id"
    )
    author: Mapped[User] = relationship("User")

    created_at: Mapped[datetime] = mapped_column()
