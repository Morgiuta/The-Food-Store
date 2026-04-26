from sqlmodel import SQLModel


class PublicSchema(SQLModel):
    model_config = {"from_attributes": True}
