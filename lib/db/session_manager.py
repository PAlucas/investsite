from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

_session_factory: Optional[sessionmaker] = None

def set_session_factory(factory: sessionmaker):
    global _session_factory
    _session_factory = factory

def get_session() -> Session:
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call set_session_factory() first.")
    return _session_factory()
