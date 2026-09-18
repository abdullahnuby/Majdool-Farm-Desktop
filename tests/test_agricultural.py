from app.application.agricultural_service import AgriculturalService
def test_report_validation(): assert AgriculturalService.validate_report("فحص","ملاحظة","توصية")
def test_empty_report():
    try: AgriculturalService.validate_report("","ملاحظة","توصية")
    except ValueError:return
    assert False
def test_priority(): assert AgriculturalService.priority_value("عالية")==3
