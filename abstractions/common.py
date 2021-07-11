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


def validate_distance(v, u, new_v, new_u, epsilon=0):
    old_d = get_dist(v, u)
    new_d = get_dist(new_v, new_u)
    return np.abs(new_d/old_d - 1)<= epsilon/1000000

def get_approximated(edges, new_vertices, vertices, epsilon=0):
    neighbors = defaultdict(set)

    for x, y in edges:
        #if x > y:
        neighbors[x].add(y)
        #else:
        neighbors[y].add(x)
    
    sequences = []
    for i, (x, y) in enumerate(new_vertices):
        xa, xb = int(np.floor(x)), int(np.ceil(x))
        ya, yb = int(np.floor(y)), int(np.ceil(y))
        variants = [(xa, ya)]
        if ya != yb:
            variants.append((xa, yb))
        if xa != xb:
            variants.append((xb, ya))
            if ya!=yb:
                variants.append((xb, yb))
        # print(i, variants)
        if i == 0:
            new_sequences = []
            for v in variants:
                new_sequences.append([v])
            sequences = new_sequences
            continue
        new_sequences = []
        for prefix in sequences:
            for v in variants:
                neigh = [s for s in neighbors[i] if s < i]
                val_results = [
                    validate_distance(vertices[s], vertices[i], prefix[s], v, epsilon=epsilon)
                    for s in neigh
                ] + [True]
                if not np.all(val_results):
                    continue

                new_sequences.append(prefix + [v])
                # print(i, prefix, v, neighbors[i])
        sequences = new_sequences
    return sequences

def get_best_sequences(approx_sequences, data):
    new_seq = []
    min_dist = None
    for seq in approx_sequences:
        dist_data = [
            np.min([get_dist(p, q) for q in seq])
            for p in data['hole']
        ]
        dist = np.sum(dist_data)
        if min_dist is None or min_dist > dist:
            min_dist = dist
            new_seq = [seq]
        elif dist == min_dist:
            new_seq.append(seq)
    return min_dist, new_seq


if __name__ == "__main__":
    # some checks
    print(sums([1, 1]))
    print(sums([1, 1], [3, 3]))
    print(means([1, 1]))
    print(means([1, 1], [3, 3]))