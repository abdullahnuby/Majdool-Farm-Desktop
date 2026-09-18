class InventoryService:
    @staticmethod
    def signed_quantity(movement_type, quantity):
        if quantity < 0:
            raise ValueError("الكمية لا يمكن أن تكون سالبة.")
        positive={"استلام_شراء","إضافة","إرجاع_صرف","تحويل_داخل","تسوية_زيادة"}
        return quantity if movement_type in positive else -quantity

    @staticmethod
    def balance(movements):
        return sum(InventoryService.signed_quantity(x.movement_type,x.quantity) for x in movements)

    @staticmethod
    def can_issue(balance, quantity):
        if quantity <= 0: raise ValueError("كمية الصرف يجب أن تكون أكبر من صفر.")
        if balance < quantity:
            raise ValueError("الرصيد غير كافٍ للصرف.")
        return True
