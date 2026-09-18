from app.infrastructure.consultant_repository import ConsultantRepository


def test_consultant_update_requires_name():
    try:
        ConsultantRepository().update_consultant(1, " ", "زراعي")
    except ValueError as error:
        assert "اسم الاستشاري" in str(error)
    else:
        assert False
