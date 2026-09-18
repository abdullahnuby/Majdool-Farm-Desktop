class AgriculturalService:
    @staticmethod
    def validate_report(title,findings,recommendations):
        if not title.strip(): raise ValueError("عنوان التقرير مطلوب.")
        if not findings.strip(): raise ValueError("الملاحظات مطلوبة.")
        if not recommendations.strip(): raise ValueError("التوصيات مطلوبة.")
        return True
    @staticmethod
    def priority_value(priority):
        values={"منخفضة":1,"متوسطة":2,"عالية":3,"عاجلة":4}
        if priority not in values: raise ValueError("درجة الأولوية غير صحيحة.")
        return values[priority]
