from app.infrastructure.repositories import FarmRepository
class FarmService:
 def __init__(self,repo=None):self.repo=repo or FarmRepository()
 def create(self,name,location,area,unit,notes):
  if not name.strip():raise ValueError("اسم المزرعة مطلوب.")
  return self.repo.create(name,location,area,unit,notes)
