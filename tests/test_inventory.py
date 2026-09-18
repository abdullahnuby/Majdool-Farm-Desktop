from app.application.inventory_service import InventoryService
class M:
    def __init__(self,t,q): self.movement_type=t; self.quantity=q
def test_balance():
    assert InventoryService.balance([M("استلام_شراء",100),M("صرف",30),M("إرجاع_صرف",5)])==75
def test_negative_issue_rejected():
    try: InventoryService.can_issue(10,11)
    except ValueError: return
    assert False
def test_negative_quantity_rejected():
    try: InventoryService.signed_quantity("استلام_شراء",-1)
    except ValueError: return
    assert False


def test_item_update_requires_name():
    from app.infrastructure.inventory_repository import InventoryRepository
    try: InventoryRepository().update_item(1, " ", "عام", "وحدة", 0)
    except ValueError as error: assert "اسم الصنف" in str(error)
    else: assert False
