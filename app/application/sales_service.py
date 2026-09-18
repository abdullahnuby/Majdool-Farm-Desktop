class SalesService:
 @staticmethod
 def line_total(qty,price):
  if qty<0 or price<0: raise ValueError("الكمية والسعر لا يمكن أن يكونا سالبين.")
  return qty*price
 @staticmethod
 def invoice_total(subtotal,discount=0,tax=0):
  if discount<0 or tax<0 or discount>subtotal: raise ValueError("الخصم أو الضريبة غير صحيحة.")
  return subtotal-discount+tax
 @staticmethod
 def outstanding(total,receipts):
  if total<0 or receipts<0: raise ValueError("القيم غير صحيحة.")
  return max(0,total-receipts)
