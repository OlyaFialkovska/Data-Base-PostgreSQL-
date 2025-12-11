from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from orm_base import Base


class Platform(Base):
    __tablename__ = "Platform_"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column("name", String, nullable=False)
    creation_date = Column("creation date", Date, nullable=False)


class Freelancer(Base):
    __tablename__ = "Freelancer_"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column("Name", String(30), nullable=False)
    surname = Column("Surname", String(30), nullable=False)
    email = Column("Email", String(30), nullable=False)
    password = Column("Password", String(30), nullable=False)

    # 1:M — фрілансер виконує багато проєктів
    projects = relationship("Project", back_populates="freelancer")


class Customer(Base):
    __tablename__ = "Customer_"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column("Name", String(30), nullable=False)
    surname = Column("Surname", String(30), nullable=False)
    email = Column("Email", String(30), nullable=False)
    password = Column("Password", String(30), nullable=False)

    # 1:M — замовник створює багато проєктів
    projects = relationship("Project", back_populates="customer")


class Project(Base):
    __tablename__ = "Project_"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    name = Column("Name", String(20), nullable=False)
    deadline = Column("Deadline", Date, nullable=False)
    start_date = Column("Start date", Date, nullable=False)
    end_date = Column("End date", Date, nullable=False)

    customer_id = Column(
        "Customer_id",
        Integer,
        ForeignKey("public.Customer_.id"),
        nullable=True,
    )
    freelancer_id = Column(
        "Freelancer_id",
        Integer,
        ForeignKey("public.Freelancer_.id"),
        nullable=True,
    )

    customer = relationship("Customer", back_populates="projects")
    freelancer = relationship("Freelancer", back_populates="projects")


class FreelancerPlatform(Base):
    __tablename__ = "Freelancer_Platform_"
    __table_args__ = {"schema": "public"}

    freelancer_id = Column(
        "Freelancer_id",
        Integer,
        ForeignKey('public."Freelancer_".id'),
        primary_key=True,
    )
    platform_id = Column(
        "Platform_id",
        Integer,
        ForeignKey('public."Platform_".id'),
        primary_key=True,
    )


class CustomerPlatform(Base):
    __tablename__ = "Customer_Platform_"
    __table_args__ = {"schema": "public"}

    customer_id = Column(
        "Customer_id",
        Integer,
        ForeignKey('public."Customer_".id'),
        primary_key=True,
    )
    platform_id = Column(
        "Platform_id",
        Integer,
        ForeignKey('public."Platform_".id'),
        primary_key=True,
    )
