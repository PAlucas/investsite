from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from lib.db.models.base import Base

class Stocks(Base):
    """
    Model representing stock information.
    Equivalent to the Django Stocks model in the original application.
    Now inherits from Base with UUID primary key and timestamps.
    """
    __tablename__ = 'stocks'
    
    # No need to redefine id as it's inherited from Base
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(String(255), nullable=True)
    url_news: Mapped[str] = mapped_column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<Stock {self.code}: {self.name}>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'company': self.company,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }
