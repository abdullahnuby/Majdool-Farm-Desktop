from app.application.purchase_service import PurchaseService
def test_line(): assert PurchaseService.line_total(4,25)==100
def test_total(): assert PurchaseService.invoice_total(1000,100,50)==950
def test_due(): assert PurchaseService.outstanding(950,300)==650
def test_bad_discount():
    try: PurchaseService.invoice_total(100,101,0)
    except ValueError:return
    assert False

def test_supplier_update_requires_name():
    from app.infrastructure.purchase_repository import PurchaseRepository
    try: PurchaseRepository().update_supplier(1, " ")
    except ValueError as error: assert "اسم المورد" in str(error)
    else: assert False
