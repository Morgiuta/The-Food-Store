from sqlmodel import Session


class UnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self._session.rollback()
            return

        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
