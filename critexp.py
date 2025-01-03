from scipy.optimize import root_scalar

def solve_for_d(x: float, y: float, z: float) -> float:
    """
    Solve for d in the equation x^d + y^d + z^d = 1.
    
    Args:
        x (float): Value of x, must be in the range (0, 1].
        y (float): Value of y, must be in the range (0, 1].
        z (float): Value of z, must be in the range (0, 1].
        
    Returns:
        float: The solution for d.
        
    Raises:
        ValueError: If x, y, or z is not in the range (0, 1].
    """
    # Check if inputs are valid
    if not (0 < x <= 1 and 0 < y <= 1 and 0 < z <= 1):
        raise ValueError("x, y, and z must all be in the range (0, 1].")

    # Define the equation
    def equation(d):
        return x**d + y**d + z**d - 1

    # Solve using root_scalar with a reasonable bracket
    bracket = [0.1, 10]  # Search for d in this range
    result = root_scalar(equation, bracket=bracket, method='bisect')

    # Check if the solver succeeded
    if not result.converged:
        raise RuntimeError("Failed to converge to a solution for d.")

    return result.root