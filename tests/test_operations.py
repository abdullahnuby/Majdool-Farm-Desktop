import pytest

from app.infrastructure.operations_repository import OperationsRepository


def test_operation_requires_type():
    with pytest.raises(ValueError, match="نوع العملية مطلوب"):
        OperationsRepository().add_operation(" ")


def test_operation_rejects_negative_cost():
    with pytest.raises(ValueError, match="التكلفة لا يمكن أن تكون سالبة"):
        OperationsRepository().add_operation("ري", cost=-1)


def test_asset_requires_code_and_name():
    with pytest.raises(ValueError, match="كود واسم الأصل مطلوبان"):
        OperationsRepository().add_asset("", "")


def test_maintenance_order_requires_title():
    with pytest.raises(ValueError, match="عنوان أمر الصيانة مطلوب"):
        OperationsRepository().add_order(" ")


def test_asset_update_requires_name():
    with pytest.raises(ValueError, match="اسم الأصل مطلوب"):
        OperationsRepository().update_asset(1, " ", "معدات", "متاح")
