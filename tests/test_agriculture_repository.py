import pytest

from app.infrastructure.agriculture_repository import AgricultureRepository


def test_irrigation_requires_positive_quantity():
    with pytest.raises(ValueError, match="كمية الري"):
        AgricultureRepository().add_irrigation(0)


def test_irrigation_requires_method():
    with pytest.raises(ValueError, match="طريقة الري"):
        AgricultureRepository().add_irrigation(10, method=" ")


def test_fertilization_requires_product():
    with pytest.raises(ValueError, match="اسم السماد"):
        AgricultureRepository().add_fertilization(" ", 10)


def test_fertilization_requires_positive_quantity():
    with pytest.raises(ValueError, match="كمية السماد"):
        AgricultureRepository().add_fertilization("سماد عضوي", 0)