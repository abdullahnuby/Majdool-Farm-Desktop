from app.application.sales_service import SalesService
def test_line_total(): assert SalesService.line_total(10,25)==250
def test_invoice_total(): assert SalesService.invoice_total(1000,100,45)==945
def test_outstanding(): assert SalesService.outstanding(1000,350)==650
def test_invalid_discount():
 try: SalesService.invoice_total(100,101,0)
 except ValueError:return
 assert False

def test_customer_update_requires_name():
 from app.infrastructure.sales_repository import SalesRepository
 try: SalesRepository().update_customer(1, " ")
 except ValueError as error: assert "اسم العميل" in str(error)
 else: assert False
