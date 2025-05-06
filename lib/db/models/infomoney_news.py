from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, DateTime, ForeignKey
from datetime import datetime
from lib.db.models.base import Base

class InfomoneyNews(Base):
    """
    Model representing news articles from Infomoney.
    Follows the clean architecture pattern with UUID primary key and timestamps.
    """
    __tablename__ = 'infomoney_news'
    
    # No need to redefine id as it's inherited from Base
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    published_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    stock_id: Mapped[str] = mapped_column(String, ForeignKey('stocks.id'), nullable=True)
    
    def __repr__(self):
        return f"<InfomoneyNews {self.id}: {self.title or self.url[:30]}>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'stock_id': self.stock_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }
