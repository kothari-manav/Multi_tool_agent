from tools.employee_tool import employee_lookup, employee_count_by_department
from tools.percentage_tool import percentage_calculation


def test_employee_lookup_found():
    assert "Engineering" in employee_lookup.invoke({"name": "John Doe"})


def test_employee_lookup_missing():
    assert "No employee" in employee_lookup.invoke({"name": "Nobody"})


def test_count_empty_department():
    assert "0 out of" in employee_count_by_department.invoke({"department": "Marketing"})


def test_percentage_of():
    assert percentage_calculation.invoke({"percentage": 20, "number": 30}) == "6.00"