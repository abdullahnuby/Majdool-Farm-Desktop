class PurchaseService:
    @staticmethod
    def line_total(quantity,unit_price):
        if quantity<=0 or unit_price<0: raise ValueError("الكمية أو السعر غير صحيح.")
        return quantity*unit_price
    @staticmethod
    def invoice_total(subtotal,discount=0,tax=0):
        if subtotal<0 or discount<0 or tax<0 or discount>subtotal: raise ValueError("قيم الفاتورة غير صحيحة.")
        return subtotal-discount+tax
    @staticmethod
    def outstanding(total,paid):
        if total<0 or paid<0: raise ValueError("القيم غير صحيحة.")
        return max(0,total-paid)
