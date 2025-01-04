

def bisection(f, a, b, tol=1e-6):
    #print(f"a: {f(a)}, b: {f(b)}")
    if f(a) * f(b) >= 0:
        return b
    while (b - a) / 2 > tol:
        c = (a + b) / 2
        if f(c) == 0:
            return c
        elif f(a) * f(c) < 0:
            b = c
        else:
            a = c
    return (a + b) / 2



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

    result = bisection(equation, 0, 2)

    return result