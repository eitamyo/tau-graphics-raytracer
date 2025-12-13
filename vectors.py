def normalize(vector):
    norm = sum([component ** 2 for component in vector]) ** 0.5
    return [component / norm for component in vector]

def cross(a, b):
    c = [a[1]*b[2] - a[2]*b[1],
         a[2]*b[0] - a[0]*b[2],
         a[0]*b[1] - a[1]*b[0]]

    return c

def dot(a, b):
    return sum([a[i] * b[i] for i in range(3)])