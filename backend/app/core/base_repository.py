from typing import Generic, Type, TypeVar

from sqlmodel import SQLModel, Session, select

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: Type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, record_id) -> ModelT | None:
        if isinstance(record_id, tuple):
            return self.session.get(self.model, record_id)
        return self.session.get(self.model, record_id)

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def get_all(self, offset: int = 0, limit: int = 20) -> list[ModelT]:
        return list(
            self.session.exec(
                select(self.model).offset(offset).limit(limit)
            ).all()
        )
