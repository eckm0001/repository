from typing import Type, Optional
from contextlib import contextmanager
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import URL
from sqlalchemy import select
from models import Base, Users, Devices, InterfaceNames, Interfaces
from models import StackData, Models, Vendors
#import models as models
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_url: URL):
        self.engine = create_engine(db_url, echo=False)
        self.connection = self.engine.connect()
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self, *models: Type[Base]):
        Base.metadata.create_all(self.engine) #, tables=[(model.__table__) for model in models])

    def get_or_create_user(self, session: Session, username: str, password: str) -> Users:
        user = session.query(Users).filter_by(username=username).first()
        if not user:
            user = Users(username=username, password=password)
            session.add(user)
            session.commit()
        return user

    def insert_or_update_device(self, session: Session, device_data: dict):
        device = session.query(Devices).filter_by(name=device_data['name']).first()
        if device:
            for key, value in device_data.items():
                setattr(device, key, value)
        else:
            device = Devices(**device_data)
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

def get_inventory(sess, conf):
    defaults = {'username': conf['env']['app_cred_u1'], 'password': conf['env']['app_cred_p1']}
    users = sess.execute(
        select(Users).where(Users.username.in_([defaults['username']]))
    ).first()[0]
    username = users.username
    password = users.password
    devices = sess.execute(
        select(Devices)
    ).fetchall()
    inv = {}
    for line in devices:
        if line.Devices.enabled:
            inv[line.Devices.name] = {
                "name": line.Devices.name,
                "connection_options": {
                    "napalm": {
                        "hostname": line.Devices.hostname,
                        "port": 22,
                        "username": username,
                        "password": password,
                        "platform": line.Devices.platform
                    }
                },
                "enabled": line.Devices.enabled
            }
    logger.info(inv)
    return inv
