from sqlalchemy import delete

from app.database.db import SessionLocal
from app.domain.models import Block, Farm, Sector
from app.infrastructure.repositories import FarmRepository, StructureRepository


def _reset_structure():
    with SessionLocal() as session:
        session.execute(delete(Block))
        session.execute(delete(Sector))
        session.execute(delete(Farm))
        session.commit()


def test_structure_crud_and_validation():
    _reset_structure()
    farm_repo = FarmRepository()
    structure_repo = StructureRepository()

    farm = farm_repo.create("مزرعة شمال", "المدينة", 12, "فدان", "ملاحظات")
    sector = structure_repo.create_sector(farm.id, "قطاع 1")
    block = structure_repo.create_block(sector.id, "B-001", "بلوك أ")

    updated_farm = farm_repo.update_farm(farm.id, "مزرعة شمال الجديدة", "المنطقة", 14, "هكتار", "تعديل")
    updated_sector = structure_repo.update_sector(sector.id, "قطاع 1 محدث")
    updated_block = structure_repo.update_block(block.id, "B-002", "بلوك أ محدث", 8, 200, "ملاحظات")

    assert updated_farm.name == "مزرعة شمال الجديدة"
    assert updated_sector.name == "قطاع 1 محدث"
    assert updated_block.code == "B-002"
    assert updated_block.palm_count == 200

    try:
        farm_repo.delete_farm(farm.id)
    except ValueError:
        pass
    else:
        assert False, "يجب منع حذف مزرعة تحتوي على قطاعات."

    structure_repo.delete_block(updated_block.id)
    structure_repo.delete_sector(updated_sector.id)
    farm_repo.delete_farm(updated_farm.id)
