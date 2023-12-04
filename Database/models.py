from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from enum import Enum as EnumClass

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    user_state = Column(Boolean, default=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    username = Column(String(100))
    language_code = Column(String(10))
    registration_date = Column(DateTime(timezone=True), default=func.now())

    # Relationship with ads
    ads = relationship("Ad", back_populates="user")


class AdStatusEnum(EnumClass):
    pending = "pending"
    completed = "completed"
    canceled = "canceled"


class Ad(Base):
    __tablename__ = 'ads'

    id = Column(Integer, primary_key=True, nullable=False, unique=True, autoincrement=True)
    ad_status = Column(Enum(AdStatusEnum), nullable=False, default=AdStatusEnum.pending)
    category = Column(String(100), nullable=False)
    data = Column(String, nullable=False)

    # Foreign key relationship with users
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="ads")
