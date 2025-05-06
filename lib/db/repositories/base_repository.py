from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union
from sqlalchemy import select, update, delete, func, create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from lib.db.models.base import Base
from lib.db.session_manager import get_session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    """
    Base repository class that provides common CRUD operations for all models.
    Uses SQLAlchemy for database operations and follows the repository pattern.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository with the model class it will be working with.
        
        Args:
            model_class: The SQLAlchemy model class this repository will handle
        """
        self.model_class = model_class
        self.session = get_session()
    
    def create(self, **kwargs) -> T:
        """
        Create a new instance of the model with the given attributes.
        
        Args:
            **kwargs: Attributes to set on the new instance
            
        Returns:
            The created model instance
        """
        instance = self.model_class(**kwargs)
        
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
            
        return instance
    
    def create_many(self, items: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple instances of the model.
        
        Args:
            items: List of dictionaries containing attributes for each instance
            
        Returns:
            List of created model instances
        """
        instances = [self.model_class(**item) for item in items]
        
        self.session.add_all(instances)
        self.session.commit()
        
        # Refresh all instances to get generated values
        for instance in instances:
            self.session.refresh(instance)
                
        return instances
    
    def find_by_id(self, id: str) -> Optional[T]:
        """
        Find a model instance by its ID.
        
        Args:
            id: The ID of the instance to find
            
        Returns:
            The found instance or None if not found
        """
        stmt = select(self.model_class).where(
            self.model_class.id == id,
            self.model_class.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalar_one_or_none()
    
    def find_all(self) -> List[T]:
        """
        Find all non-deleted instances of the model.
        
        Returns:
            List of all non-deleted model instances
        """
        stmt = select(self.model_class).where(
            self.model_class.deleted_at.is_(None)
        )
        return self.session.execute(stmt).scalars().all()
    
    def find_by(self, **kwargs) -> List[T]:
        """
        Find model instances matching the given criteria.
        
        Args:
            **kwargs: Criteria to filter by
            
        Returns:
            List of matching model instances
        """
        filters = []
        
        # Add each filter condition
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                attr = getattr(self.model_class, key)
                filters.append(attr == value)
        
        # Always filter out deleted records
        filters.append(self.model_class.deleted_at.is_(None))
        
        stmt = select(self.model_class).where(*filters)
        return self.session.execute(stmt).scalars().all()
    
    def find_one_by(self, **kwargs) -> Optional[T]:
        """
        Find a single model instance matching the given criteria.
        
        Args:
            **kwargs: Criteria to filter by
            
        Returns:
            The first matching instance or None if not found
        """
        filters = []
        
        # Add each filter condition
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                attr = getattr(self.model_class, key)
                filters.append(attr == value)
        
        # Always filter out deleted records
        filters.append(self.model_class.deleted_at.is_(None))
        
        stmt = select(self.model_class).where(*filters)
        return self.session.execute(stmt).scalar_one_or_none()
    
    def update(self, id: str, **kwargs) -> Optional[T]:
        """
        Update a model instance with the given attributes.
        
        Args:
            id: The ID of the instance to update
            **kwargs: Attributes to update
            
        Returns:
            The updated instance or None if not found
        """
        # First find the instance to update
        stmt = select(self.model_class).where(
            self.model_class.id == id,
            self.model_class.deleted_at.is_(None)
        )
        instance = self.session.execute(stmt).scalar_one_or_none()
        
        if instance:
            # Update the instance attributes
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self.session.commit()
            self.session.refresh(instance)
            
        return instance
    
    def delete(self, id: str) -> bool:
        """
        Hard delete a model instance.
        
        Args:
            id: The ID of the instance to delete
            
        Returns:
            True if the instance was deleted, False otherwise
        """
        stmt = delete(self.model_class).where(self.model_class.id == id)
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0
    
    def soft_delete(self, id: str) -> bool:
        """
        Soft delete a model instance by setting its deleted_at timestamp.
        
        Args:
            id: The ID of the instance to soft delete
            
        Returns:
            True if the instance was soft deleted, False otherwise
        """
        stmt = update(self.model_class).where(
            self.model_class.id == id,
            self.model_class.deleted_at.is_(None)
        ).values(deleted_at=datetime.now())
        
        result = self.session.execute(stmt)
        self.session.commit()
        return result.rowcount > 0
    
    def count(self, **kwargs) -> int:
        """
        Count the number of model instances matching the given criteria.
        
        Args:
            **kwargs: Criteria to filter by
            
        Returns:
            The count of matching instances
        """
        filters = []
        
        # Add each filter condition
        for key, value in kwargs.items():
            if hasattr(self.model_class, key):
                attr = getattr(self.model_class, key)
                filters.append(attr == value)
        
        # Always filter out deleted records
        filters.append(self.model_class.deleted_at.is_(None))
        
        stmt = select(func.count()).select_from(self.model_class).where(*filters)
        return self.session.execute(stmt).scalar_one()
    
    def exists(self, **kwargs) -> bool:
        """
        Check if any model instances match the given criteria.
        
        Args:
            **kwargs: Criteria to filter by
            
        Returns:
            True if any matching instances exist, False otherwise
        """
        return self.count(**kwargs) > 0
        
    def get_all_filtered(self, filters: Dict[str, Any], order_by: str = None, descending: bool = False) -> List[T]:
        """
        Get all non-deleted instances of the model matching the given filters with optional ordering.
        
        Args:
            filters: Dictionary of filters to apply. Can contain special operators like 'in_' and 'not_in'
            order_by: Optional column name to order by
            descending: Whether to order in descending order (default: False)
            
        Returns:
            List of matching model instances
        """
        # Start with a base query that filters out deleted records
        query_filters = [self.model_class.deleted_at.is_(None)]
        
        # Apply filters dynamically
        for key, condition in filters.items():
            if hasattr(self.model_class, key):
                column_attr = getattr(self.model_class, key)
                
                # Handle 'in_' and 'not_in' conditions
                if isinstance(condition, dict):
                    if "in_" in condition:
                        query_filters.append(column_attr.in_(condition["in_"]))
                    elif "not_in" in condition:
                        query_filters.append(~column_attr.in_(condition["not_in"]))
                else:
                    query_filters.append(column_attr == condition)
        
        # Create the select statement with all filters
        stmt = select(self.model_class).where(*query_filters)
        
        # Apply ordering if specified
        if order_by and hasattr(self.model_class, order_by):
            order_column = getattr(self.model_class, order_by)
            if descending:
                stmt = stmt.order_by(order_column.desc())
            else:
                stmt = stmt.order_by(order_column)
        
        # Execute the query and return the results
        return self.session.execute(stmt).scalars().all()
