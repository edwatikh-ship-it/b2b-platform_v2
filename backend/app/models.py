from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class RequestStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    MODERATION = "moderation"
    COMPLETED = "completed"


class URLStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("RequestItem", back_populates="request", cascade="all, delete-orphan")
    search_results = relationship("SearchResultFromDB", back_populates="request", cascade="all, delete-orphan")
    parsing_tasks = relationship("ParsingTask", back_populates="request", cascade="all, delete-orphan")


class RequestItem(Base):
    __tablename__ = "request_items"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    pos = Column(Integer, nullable=False)
    name = Column(String(500), nullable=False)
    unit = Column(String(50))
    qty = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("Request", back_populates="items")
    search_results = relationship("SearchResultFromDB", back_populates="item", cascade="all, delete-orphan")
    parsing_task = relationship("ParsingTask", back_populates="item", uselist=False, cascade="all, delete-orphan")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    company_name = Column(String(500))
    inn = Column(String(12), index=True)
    rating = Column(Float, default=0.0)
    source = Column(String(50), default="database")  # "database" или "parsing"
    created_at = Column(DateTime, default=datetime.utcnow)

    contacts = relationship("Contact", back_populates="supplier", cascade="all, delete-orphan")
    search_results = relationship("SearchResultFromDB", back_populates="supplier", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    name = Column(String(255))
    phone = Column(String(20), index=True)
    email = Column(String(255), index=True)
    position = Column(String(255))
    source = Column(String(50), default="database")
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="contacts")
    search_results = relationship("SearchResultFromDB", back_populates="contact", cascade="all, delete-orphan")


class SearchResultFromDB(Base):
    __tablename__ = "search_results_from_db"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("request_items.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    source = Column(String(50), default="database")
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("Request", back_populates="search_results")
    item = relationship("RequestItem", back_populates="search_results")
    supplier = relationship("Supplier", back_populates="search_results")
    contact = relationship("Contact", back_populates="search_results")


class ParsingTask(Base):
    __tablename__ = "parsing_tasks"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("request_items.id"), nullable=False)
    search_query = Column(String(500), nullable=False)
    status = Column(SQLEnum(URLStatus), default=URLStatus.PENDING)
    result_json = Column(Text)  # JSON: {urls: [...]}
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    request = relationship("Request", back_populates="parsing_tasks")
    item = relationship("RequestItem", back_populates="parsing_task")
    parsed_urls = relationship("ParsedURL", back_populates="task", cascade="all, delete-orphan")


class ParsedURL(Base):
    __tablename__ = "parsed_urls"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("parsing_tasks.id"), nullable=False)
    url = Column(String(500), nullable=False, index=True)
    title = Column(String(500))
    company_name = Column(String(500))
    raw_response = Column(Text)  # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("ParsingTask", back_populates="parsed_urls")
    moderated = relationship("ModeratedURL", back_populates="parsed_url", uselist=False, cascade="all, delete-orphan")


class ModeratedURL(Base):
    __tablename__ = "moderated_urls"

    id = Column(Integer, primary_key=True, index=True)
    parsed_url_id = Column(Integer, ForeignKey("parsed_urls.id"), nullable=False)
    url = Column(String(500), nullable=False, index=True)
    status = Column(SQLEnum(URLStatus), default=URLStatus.NEEDS_REVIEW)
    inn = Column(String(12), index=True)
    checko_data = Column(Text)  # JSON от Checko API
    contact_info = Column(Text)  # JSON: {name, phone, email}
    moderator_notes = Column(Text)
    moderated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    parsed_url = relationship("ParsedURL", back_populates="moderated")
