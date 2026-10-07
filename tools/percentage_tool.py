from langchain_core.tools import tool

@tool
def percentage_calculation(percentage: float, number: float) -> str:
    """Calculates what a given percentage OF a number is.
    Use this when the user asks 'what is X% of Y', not when they ask 'what percent is X of Y'.
    Example: 'What is 20% of 30?' -> percentage=20, number=30 -> returns 6.00
    """
    result = (percentage / 100) * number
    return f"{result:.2f}"