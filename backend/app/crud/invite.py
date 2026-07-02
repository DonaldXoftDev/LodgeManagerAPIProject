from typing import TypeVar, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.crud.base_crud import ModelType
from app.schemas import invitation as schema_invite
from app.models.invitation import Invite


class CrudInvite:
    def __init__(self, model: Type[Invite]):
        self.model = model

    def add_invite_record(self, db: Session, invite_in: schema_invite.InviteCreate)-> Invite:
        db_invite = self.model(**invite_in.model_dump())
        db.add(db_invite)
        db.commit()
        db.refresh(db_invite)
        return db_invite

    def get_invite_record_by_id(self, db: Session, invite_id: UUID) -> Invite | None:
        options= joinedload(Invite.lodge)
        stmt = select(self.model).where(self.model.id == invite_id).options(options)
        return  db.execute(stmt).scalar()






crud_invite = CrudInvite(Invite)