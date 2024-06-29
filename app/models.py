""" models
"""
from __future__ import annotations
from typing import (
    Optional,
    List,
#    Dict,
#    Tuple,
    Any,
#    Union
)

from sqlalchemy import (
#    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Float)
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
#    relationship,
    )
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    """ class base
    """
    pass

class Users(Base):
    """ class users
    """
    __tablename__ = 'users_table'

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)

    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_on: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True)
    #devices: Mapped[Optional["Device"]] = relationship()
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', password='{self.password}'"+\
            f", created_at='{self.created_at}', updated_on='{self.updated_on}')"
    def __str__(self):
        return f"User(id={self.id}, username='{self.username}', password='{self.password}'"+\
            f", created_at='{self.created_at}', updated_on='{self.updated_on}')"

class InterfaceNames(Base):
    """ class interface names
    """
    __tablename__ = "interfacenames_table"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    abbrev: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_on: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True)

    def __repr__(self):
        return f"InterfaceName(id={self.id}, name='{self.name}', abbrev='{self.abbrev}'"+\
            f", created_at='{self.created_at}', updated_on='{self.updated_on}')"
    def __str__(self):
        return f"InterfaceName(id={self.id}, name='{self.name}', abbrev='{self.abbrev}'"+\
            f", created_at='{self.created_at}', updated_on='{self.updated_on}')"


class InterfacesData(Base):
    """ interfaces data
    """
    __tablename__ = "interfaces_table"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices_table.id"))


class StackData(Base):
    """ stack data
    """
    __tablename__ = "stackdata_table"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    interface_name_id: Mapped[Optional[int]] = mapped_column(ForeignKey('interfacenames_table.id'))
    model: Mapped[str] = mapped_column(String, nullable=False)
    os_verson: Mapped[str] = mapped_column(String, nullable=False)
    shelves: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_on: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True)


class Serials(Base):
    """ serials
    """
    __tablename__ = "serials_table"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    serial: Mapped[str] = mapped_column(String, nullable=False)
    asset: Mapped[str] = mapped_column(String, nullable=False)


class OSVersions(Base):
    """ os versions
    """
    __tablename__ = "osversions_table"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    os_version: Mapped[str] = mapped_column(String, nullable=False)

class Models(Base):
    """ models
    """
    __tablename__ = "models_table"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    model: Mapped[str] = mapped_column(String, nullable=False)

class Vendors(Base):
    """ vendors
    """
    __tablename__ = "vendors_table"
    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    vendor: Mapped[str] = mapped_column(String, nullable=False)

class Devices(Base):
    """ devices
    """
    __tablename__ = 'devices_table'

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    hostname: Mapped[str] = mapped_column(String, nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users_table.id'), default=Any|None)
    platform: Mapped[str] = mapped_column(String, nullable=True)
    groups: Mapped[List[str]] = mapped_column(String, nullable=True)
    data: Mapped[List[str]] = mapped_column(String, nullable=True)
    connection_options: Mapped[List[str]] = mapped_column(String, nullable=True)
    defaults: Mapped[List[str]] = mapped_column(String, nullable=True)
    vendor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vendors_table.id")
    )  # , default=Any|None)
    model_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("models_table.id")
    )  # , default=Any|None)
    os_version_data: Mapped[Optional[int]] = mapped_column(
        ForeignKey("osversions_table.id")
    )  # , default=Any|None)
    serial_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("serials_table.id")
    )  # , default=Any|None)
    uptime: Mapped[Float] = mapped_column(Float, default=0)
    enabled: Mapped[Boolean] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True)
    updated_on: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"Device(id={self.id}, name='{self.name}', hostname='{self.hostname}'"+\
            f", user_id='{self.user_id}', created_at='{self.created_at}'"+\
            f", updated_on='{self.updated_on}')"
    def __str__(self):
        return f"Device(id={self.id}, name='{self.name}', hostname='{self.hostname}'"+\
            f", user_id='{self.user_id}', created_at='{self.created_at}'"+\
            f", updated_on='{self.updated_on}')"
