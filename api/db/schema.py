from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)

from api.db import NAMING_CONVECTION


metadata = MetaData(naming_convention=NAMING_CONVECTION)

users = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(64), nullable=False, unique=True),
    Column("name", String(64), nullable=False),
    Column("description", Text),
    Column("email", String(120), nullable=False),
    Column("password_hash", String(192), nullable=False),
)

followers = Table(
    "followers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "from_user", Integer, ForeignKey("user.id"), nullable=False, index=True
    ),
    Column(
        "to_user", Integer, ForeignKey("user.id"), nullable=False, index=True
    ),
)

posts = Table(
    "post",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id", Integer, ForeignKey("user.id"), nullable=False, index=True
    ),
    Column("text", Text),
    Column("image", Text),
    Column("timestamp", DateTime, index=True, default=datetime.utcnow),
)

likes = Table(
    "like",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "post_id", Integer, ForeignKey("post.id"), nullable=False, index=True
    ),
    Column(
        "user_id", Integer, ForeignKey("user.id"), nullable=False, index=True
    ),
)

comments = Table(
    "comment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "post_id", Integer, ForeignKey("post.id"), nullable=False, index=True
    ),
    Column(
        "user_id", Integer, ForeignKey("user.id"), nullable=False, index=True
    ),
    Column("text", Text, nullable=False),
    Column("timestamp", DateTime, index=True, default=datetime.utcnow),
)
