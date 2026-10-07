from langchain_core.tools import tool

Employees={

    "john doe":{"department":"Engineering", "role":"Backend Developer","email": "john@company.com"},
    "jane smith": {"department": "Sales", "role": "Account Manager", "email": "jane@company.com"},
    "arjun mehta": {"department": "Engineering", "role": "ML Engineer", "email": "arjun@company.com"},

}
@tool
def employee_lookup(name: str) ->str:
    """Look up Employee's department,role,email by their name 
        Use this when employee asks for specific Employee details,department or role
        Example: 'What department is John Doe in?' -> name='John Doe'

    """
    employee=Employees.get(name.lower())
    if not employee:
        return f"No Employee with name {name} is found."
    return f"{name} works in {employee['department']} as a {employee['role']} Email : {employee['email']}"

@tool
def employee_count_by_department(department: str) -> str:
    """Counts how many employees are in a specific department, and the total employee count.
    Use this when the user asks about department headcounts, team sizes, or percentage of employees in a department.
    Example: 'How many employees are in Engineering?' -> department='Engineering'
    """
    total = len(Employees)
    in_dept = sum(1 for emp in Employees.values() if emp["department"].lower() == department.lower())
    return f"{in_dept} out of {total} total employees are in {department}."