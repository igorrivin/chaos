import numpy as np

# Step 1: Define the chaos game function with probabilities
def chaos_game_triangle(num_iterations, p1=1/3.0, p2=1/3.0, r1=1/2, r2=1/2, r3=1/2):
    # Define the vertices of the triangle
    vertices = np.array([[0, 0], [0, 1], [1, 0]])
    rlist = [r1, r2, r3]
    
    # Probabilities for selecting each vertex
    p3 = 1 - p1 - p2
    probabilities = [p1, p2, p3]
    
    # Choose a random initial point inside the triangle
    p = np.random.rand(2)
    
    # Create a list to store the points
    point_list = [p]
    
    # Perform the iterations
    for _ in range(num_iterations-1):
        # Pick a random vertex based on probabilities
        ind = np.random.choice(len(vertices), p=probabilities)
        q = vertices[ind]
        r = rlist[ind]
        # Compute the midpoint
        p = r * p + (1-r) * q
        point_list.append(p)
    
    pointarray = np.array(point_list)
    indexed_array = np.column_stack((np.arange(num_iterations), pointarray))
    return indexed_array