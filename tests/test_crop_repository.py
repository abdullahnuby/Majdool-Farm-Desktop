import pytest

from app.infrastructure.crop_repository import CropRepository


def test_season_requires_name():
    with pytest.raises(ValueError, match="اسم الموسم"):
        CropRepository().add_season(" ")


def test_batch_requires_positive_quantity():
    with pytest.raises(ValueError, match="كمية الحصاد"):
        CropRepository().add_batch(1, 1, 0)


def test_batch_requires_season_and_block():
    with pytest.raises(ValueError, match="الموسم والبلوك"):
        CropRepository().add_batch(0, 1, 10)