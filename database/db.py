from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

DATABASE_URL = "sqlite:///fitai.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    diet_type = Column(String(30), nullable=False)
    activity_level = Column(String(30), nullable=False)
    fitness_goal = Column(String(30), nullable=False)
    diseases = Column(String(200), default="None")
    allergies = Column(String(200), default="None")
    region = Column(String(100), default="Indian")
    created_at = Column(DateTime, default=datetime.utcnow)
    bmi = Column(Float)
    calorie_target = Column(Integer)


class RecommendationDB(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String(100))
    diet_plan = Column(Text)
    workout_plan = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_user_profile(profile_data: dict) -> int:
    db = SessionLocal()
    try:
        user = UserDB(**profile_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def save_recommendation(user_id: int, user_name: str, diet_plan: dict, workout_plan: dict) -> None:
    db = SessionLocal()
    try:
        rec = RecommendationDB(
            user_id=user_id,
            user_name=user_name,
            diet_plan=json.dumps(diet_plan),
            workout_plan=json.dumps(workout_plan)
        )
        db.add(rec)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_all_users() -> list:
    db = SessionLocal()
    try:
        return db.query(UserDB).order_by(UserDB.created_at.desc()).all()
    finally:
        db.close()


def get_user_recommendations(user_id: int) -> list:
    db = SessionLocal()
    try:
        recs = db.query(RecommendationDB)\
                 .filter(RecommendationDB.user_id == user_id)\
                 .order_by(RecommendationDB.created_at.desc()).all()
        return [{"id": r.id, "created_at": r.created_at,
                 "diet_plan": json.loads(r.diet_plan) if r.diet_plan else {},
                 "workout_plan": json.loads(r.workout_plan) if r.workout_plan else {}}
                for r in recs]
    finally:
        db.close()


def get_total_users_count() -> int:
    db = SessionLocal()
    try:
        return db.query(UserDB).count()
    finally:
        db.close()