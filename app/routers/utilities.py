from http import HTTPStatus

from fastapi.exceptions import HTTPException
from sqlmodel import Session

from app.models.division import Division, DivisionCreate, DivisionRead


def upsert_division(*, session: Session, division_data: DivisionCreate) -> DivisionRead:
    """Updates/inserts a division data record."""
    if division_data.id is None:  # create new division
        division_db = Division.from_orm(division_data)
    else:  # update existing division
        division_db = session.get(Division, division_data.id)
        if not division_db:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Division (id={division_data.id}) not found",
            )
        division_dict = division_data.dict(exclude_unset=True)
        for key, value in division_dict.items():
            setattr(division_db, key, value)
    session.add(division_db)
    session.commit()
    session.refresh(division_db)
    return division_db
