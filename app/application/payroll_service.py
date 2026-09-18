class PayrollService:
    @staticmethod
    def net_salary(base, additions=0, deductions=0, advances=0):
        if any(v < 0 for v in [base, additions, deductions, advances]):
            raise ValueError("القيم المالية لا يمكن أن تكون سالبة.")
        return base + additions - deductions - advances

    @staticmethod
    def assignment_cost(quantity, rate):
        if quantity < 0 or rate < 0:
            raise ValueError("الكمية والأجر غير صحيحين.")
        return quantity * rate

    @staticmethod
    def remaining_advance(amount, recovered):
        if amount < 0 or recovered < 0 or recovered > amount:
            raise ValueError("السلفة أو المسدد غير صحيح.")
        return amount - recovered
