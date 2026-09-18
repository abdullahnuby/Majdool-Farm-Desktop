from app.application.payroll_service import PayrollService
def test_net_salary(): assert PayrollService.net_salary(10000,500,300,1000)==9200
def test_assignment_cost(): assert PayrollService.assignment_cost(3,250)==750
def test_advance_remaining(): assert PayrollService.remaining_advance(1000,250)==750
