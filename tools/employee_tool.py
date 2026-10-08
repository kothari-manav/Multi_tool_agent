from langchain_core.tools import tool

Employees={

    "john doe":{"department":"Engineering", "role":"Backend Developer","email": "john@company.com"},
    "jane smith": {"department": "Sales", "role": "Account Manager", "email": "jane@company.com"},
    "arjun mehta": {"department": "Engineering", "role": "ML Engineer", "email": "arjun@company.com"},

}
@tool
def employee_lookup(name: str) -> str:
    """Looks up an employee's department, role, and email by their full name.
    Use this when the user asks about a specific employee's details, department, role, or email.
    Example: 'What department is John Doe in?' -> name='John Doe'
    """
    employee = Employees.get(name.lower())
    if not employee:
        return f"No employee with name {name} was found. This is a final answer."
    return f"{name} works in {employee['department']} as a {employee['role']}. Email: {employee['email']}"

@tool
def employee_count_by_department(department: str) -> str:
    """Counts employees in a specific department, and returns the total employee count.
    Use this when the user asks about department headcounts, team sizes, or the percentage of employees in a department.
    A count of 0 is a valid, final answer, not an error. Do not call this tool again.
    """
    total = len(Employees)
    in_dept = sum(1 for emp in Employees.values() if emp["department"].lower() == department.lower())
    return f"{in_dept} out of {total} total employees are in {department}."