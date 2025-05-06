from sqlalchemy.orm import DeclarativeBase
import uuid
import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    __abstract__ = True  # Prevents this class from being mapped as a table

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    deleted_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def serialize(self):
        """Convert the model instance to a dictionary."""
        serialized_data = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime.datetime):
                serialized_data[key] = value.isoformat()  # Convert datetime to ISO format
            elif hasattr(value, 'serialize') and callable(getattr(value, 'serialize')):
                serialized_data[key] = value.serialize()  # Recursively serialize related objects if needed
            else:
                serialized_data[key] = value  # Handle other serializable types
        # Remove the SQLAlchemy's internal attributes if needed
        serialized_data.pop('_sa_instance_state', None)
        return serialized_data