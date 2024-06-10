from typing import Type, Optional
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from models import Base, User, Device

class DatabaseManager:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url, echo=False)
        self.connection = self.engine.connect()
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self, *models: Type[Base]):
        Base.metadata.create_all(self.engine, tables=[model.__table__ for model in models])

    def get_or_create_user(self, session: Session, username: str, password: str) -> User:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username, password=password)
            session.add(user)
            session.commit()
        return user

    def insert_or_update_device(self, session: Session, device_data: dict):
        device = session.query(Device).filter_by(name=device_data['name']).first()
        if device:
            for key, value in device_data.items():
                setattr(device, key, value)
        else:
            device = Device(**device_data)
            session.add(device)
        session.commit()

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
