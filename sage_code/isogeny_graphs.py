"""isogeny_graphs.py

    Here we check for "unrecorded" isogenies; see Section 9 of the paper

"""

# We collect the j-invariants whose isogeny graphs we need to construct

my_js_213 = [-1159088625/2097152, -189613868625/128,3375/2,-140625/8, -884736, -882216989/131072, -297756989/2,-3375, 16581375, -32768, -24729001, -121, -9317, -162677523113838677, -884736000, -147197952000, -262537412640768000]
my_js_438 = [-884736, -882216989/131072, -297756989/2, -32768, -24729001, -121, -9317, -162677523113838677, -884736000, -147197952000, -262537412640768000]

# Obtainining the unrecorded isogeny degrees is then done as follows

def get_unrecorded_isogenies(d, my_js):

    K.<a> = QuadraticField(d)
    unrecorded_isogeny_degrees = set()
    for j in my_js:
        E = EllipticCurve_from_j(j).base_extend(K)
        unrecorded_isogeny_degrees = unrecorded_isogeny_degrees.union(set(E.isogeny_class().matrix().list()))

    return unrecorded_isogeny_degrees

# Then run the following

# get_unrecorded_isogenies(213, my_js_213)
# get_unrecorded_isogenies(438, my_js_438)