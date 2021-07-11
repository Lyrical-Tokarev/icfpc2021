import numpy as np

def op(*arrays, operation=np.sum):
    if len(arrays) == 1:
        return arrays[0]
    return [operation(x) for x in zip(*arrays)]

def sums(*arrays):
    return op(*arrays, operation=np.sum)

def means(*arrays):
    return op(*arrays, operation=np.mean)


def get_dist(a, b):
    return np.sum([(x - y) ** 2 for x, y in zip(a, b)])

def plus(a, b):
    return [x + y for x, y in zip(a, b)]
def minus(a, b):
    return [x - y for x, y in zip(a, b)]

def dot(a, b):
    return [x*y for x, y in zip(a, b)]

def vector(a,b):
    return minus(b, a)

def mult(a, m):
    return [x*m for x in a]

def norm(a):
    m = length(a)
    return mult(a, 1./m)

def perp(a):
    return (-a[1], a[0])

def have_intersection(a, b):
    vect_a = vector(*a)
    vect_b = vector(*b)
    vect_c = vector(a[0], b[0])
    perp_a = perp(vect_a)
    d = dot(perp_a, vect_b)
    if d == 0:
        return False
    n = dot(perp_a, vect_c)
    if n < 0 or n > d:
        return False
    # return n / d


if __name__ == "__main__":
    # some checks
    print(sums([1, 1]))
    print(sums([1, 1], [3, 3]))
    print(means([1, 1]))
    print(means([1, 1], [3, 3]))