"""utils.py

Some helpful functions
"""

GENUS_ZERO_LIST = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 18, 25]
GENUS_ONE_LIST = [11, 14, 15, 17, 19, 20, 21, 24, 27, 32, 36, 49]
CLASS_NUMBER_ONE_DISCS = {-1, -2, -3, -7, -11, -19, -43, -67, -163}
AMF2 = {26, 35, 37, 39, 43, 50, 65, 67, 91, 125, 163, 169}

15, 20, 24, 27, 32, 36


def split_cartan_genus(p):
    """Computes the genus of X_s(p) from Imin Chen's "The Jacobians of
    non-split Cartan modular curves"""

    return (1 / 24) * (p ^ 2 - 8 * p + 11 - 4 * kronecker_symbol(-3, p))


def nonsplit_cartan_genus(p):
    """Computes the genus of X_ns(p) from Imin Chen's "The Jacobians of
    non-split Cartan modular curves"""

    return (1 / 24) * (
        p ^ 2 - 10 * p + 23 + 6 * kronecker_symbol(-1, p) + 4 * kronecker_symbol(-3, p)
    )


def is_atkin_lehner_divisor(d, N):

    if ZZ(d).divides(N):
        if gcd(d, N / d) == 1:
            return True
    return False


def c_i_at_2(i, Ndash, N):

    if i == 1:
        if Ndash % 4 == 1:
            if is_atkin_lehner_divisor(2, N):
                return 1
            elif ZZ(4).divides(N):
                return 0
        if Ndash % 4 == 3:
            if is_atkin_lehner_divisor(2, N):
                return 2
            elif ZZ(4).divides(N):
                return 3 + kronecker_symbol(-Ndash, 2)
            elif ZZ(8).divides(N):
                return 3 * (1 + kronecker_symbol(-Ndash, 2))

    if i == 2 and Ndash % 4 == 3:
        return 1 + kronecker_symbol(-Ndash, 2)


def c_i(i, p, Ndash, N):

    if p == 2:
        return c_i_at_2(i, Ndash, N)

    if Ndash % 4 == 3:
        return 1 + kronecker_symbol(-Ndash, p)

    else:
        return 1 + kronecker_symbol(-4 * Ndash, p)


def fixed_point_number(Ndash, N):

    assert is_atkin_lehner_divisor(Ndash, N), "Ndash does not give an AL involution"

    N_over_Ndash = ZZ(N / Ndash)

    base_contribution = (
        prod([c_i(1, p, Ndash, N) for p in N_over_Ndash.prime_divisors()])
        * ZZ(-4 * Ndash).class_number()
    )

    if Ndash == 2:
        other_contribution = prod(
            [1 + kronecker_symbol(-4, p) for p in ZZ(N / 2).prime_divisors()]
        )
    elif Ndash == 3:
        other_contribution = prod(
            [1 + kronecker_symbol(-3, p) for p in ZZ(N / 3).prime_divisors()]
        )
    elif Ndash == 4:
        all_divisors_N_over_4 = (ZZ(N / 4)).divisors()
        all_AL_divisors = [
            D for D in all_divisors_N_over_4 if is_atkin_lehner_divisor(D, (ZZ(N / 4)))
        ]
        pre_prime_power_divisor_data = [
            D.is_prime_power(get_data=True) for D in all_AL_divisors
        ]
        prime_power_divisor_data = [
            (p, nu) for p, nu in pre_prime_power_divisor_data if nu != 0
        ]
        other_contribution = prod(
            [
                p ** (nu // 2) + p ** ((nu - 1) // 2)
                for p, nu in prime_power_divisor_data
            ]
        )
    elif Ndash % 4 == 3:
        other_contribution = (
            prod([c_i(2, p, Ndash, N) for p in N_over_Ndash.prime_divisors()])
            * ZZ(-Ndash).class_number()
        )
    else:
        other_contribution = 0

    return base_contribution + other_contribution


def genus_of_quotient(N, Ndash):

    return (1 / 4) * (2 * Gamma0(N).genus() + 2 - fixed_point_number(Ndash, N))


# Some testing of the function, the following examples taken from Galbraith's thesis

assert genus_of_quotient(91, 91) == 2
assert genus_of_quotient(46, 2) == 3
assert genus_of_quotient(55, 5) == 3
assert genus_of_quotient(84, 84) == 4
assert genus_of_quotient(92, 23) == 1
assert genus_of_quotient(99, 99) == 3


def is_multiple_of(x, a_set):

    for y in a_set:
        if y.divides(x):
            return True
    return False


def remove_multiples(a_set):

    output = set()

    for x in a_set:
        aux_set = a_set - {x}
        if not is_multiple_of(x, aux_set):
            output.add(x)

    return output


def minimally_finite(d):
    """This implements Algorithm 2.2"""
    genus_one_positive_rank_list = []  # this is B(K)
    genus_one_zero_rank_list = []  # this is S_1(K) in Algorithm 2.2

    for N in GENUS_ONE_LIST:
        label = str(N) + "a1"
        E = EllipticCurve(label)  # X_0(N)
        if E.quadratic_twist(d).rank(only_use_mwrank=False) != 0:
            genus_one_positive_rank_list.append(N)
        else:
            genus_one_zero_rank_list.append(N)

    output = set(genus_one_zero_rank_list).union(AMF2)

    S3_prime = set()

    small_prime_set = prime_range(20)

    for b in genus_one_positive_rank_list:
        for p in small_prime_set:
            candidate = b * p
            if not is_multiple_of(candidate, output):
                S3_prime.add(candidate)

    S3 = remove_multiples(S3_prime)

    output = output.union(S3)
    output = list(output)
    output = sorted(output)

    return output


def minimally_finite_fast(genus_one_zero_rank_list):
    """Sage is much slower than Magma with computing ranks of ECs over NFs,
    making `minimally_finite` slow. This function gets the data for which of
    the genus 1 modular curves have positive rank over a given quadratic field.
    This is then much faster.
    """
    genus_one_positive_rank_list = [
        N for N in GENUS_ONE_LIST if not N in genus_one_zero_rank_list
    ]

    output = set(genus_one_zero_rank_list).union(AMF2)

    S3_prime = set()

    small_prime_set = prime_range(20)

    for b in genus_one_positive_rank_list:
        for p in small_prime_set:
            candidate = b * p
            if not is_multiple_of(candidate, output):
                S3_prime.add(candidate)

    S3 = remove_multiples(S3_prime)

    output = output.union(S3)
    output = list(output)
    output = sorted(output)

    return output


def is_torsion_same(p, chi, B=100, uniform=False):
    """Returns true if the plus part of J0(p) does not gain new torsion when
    base changing to K"""
    M = ModularSymbols(p)
    S = M.cuspidal_subspace()
    T = S.atkin_lehner_operator()
    S_min = (T - parent(T)(1)).kernel()
    J0_min = S_min.abelian_variety()

    d = 2

    if uniform:
        frob_poly_data = [(q, d) for q in prime_range(d + 2, B) if q != p]
    else:
        frob_poly_data = [
            (q, 1) if chi(q) == 1 else (q, d)
            for q in prime_range(d + 2, B)
            if gcd(q, p) == 1
        ]

    point_counts = []

    for q, i in frob_poly_data:
        frob_pol_q = J0_min.frobenius_polynomial(q)
        frob_mat = companion_matrix(frob_pol_q)
        point_counts.append((frob_mat**i).charpoly()(1))

    # Recall that the rational torsion on J0(p) is entirely contained in
    # the minus part (theorem of Mazur), so checking no-growth of torsion
    # in plus part is done simply as follows

    return 1 == gcd(point_counts)


def is_rank_of_twist_zero(p, chi):
    """Returns true if the rank of the twist of the plus part of J_0(p)
    by the character chi is zero"""
    ML = ModularSymbols(p, base_ring=chi.base_ring())
    SL = ML.cuspidal_subspace()
    TL = SL.atkin_lehner_operator()
    S_min_L = (TL - parent(TL)(1)).kernel()

    for S in S_min_L.decomposition():
        my_map = S.rational_period_mapping()
        w = ML([0, oo])
        wmap = my_map(w)
        if wmap != 0:
            return False
        tw = ML.twisted_winding_element(0, chi)
        twmap = my_map(tw)
        if twmap == 0:
            return False

    return True


def check_mwgp_same(p, d):
    """Checks conditions (1) and (2) of Proposition 4.1"""
    chi = kronecker_character(d)
    if is_rank_of_twist_zero(p, chi):
        if is_torsion_same(p, chi):
            return True
    return False


def search_convenient_d(d_start, d_end):
    """Searches in a range of d for whether or not d is convenient, as defined
    in Section 3 of the paper
    """
    for d in range(d_start, d_end):
        if ZZ(d).is_squarefree():
            if not d in CLASS_NUMBER_ONE_DISCS:
                if d != 1:
                    try:
                        ans = minimally_finite(d)
                        print(f"done {d}")
                    except SignalError:
                        print(f"Rank computation failed for {d}")
                        continue
                    large_vals = [d for d in ans if d > 100]
                    if sorted(large_vals) == [125, 163, 169]:
                        if check_mwgp_same(163, d):
                            print("d = {} is good".format(d))


def search_convenient_d_fast():
    """As explained in a docstring above, Sage struggles to compute ranks,
    sometimes even giving a SignalError! For this reason, a Magma computation
    was run to determine, for -500 < d < 500, which of the genus 1 modular curves
    have positive rank over Qsqrtd. The results of this computation may be found
    in `magma_code/RankData.txt`. This function then reads this data in and
    uses the `minimally_finite_fast` method above.
    """

    with open("magma_code/RankData.txt", "r") as the_file:
        the_lines = the_file.read().splitlines()

    for a_line in the_lines:

        d, pre_rank_zero_list = a_line.split(":")
        d = Integer(d)
        rank_zero_list = eval(pre_rank_zero_list)
        rank_zero_list = [Integer(x) for x in rank_zero_list]
        ans = minimally_finite_fast(rank_zero_list)
        large_vals = [d for d in ans if d > 100]
        if sorted(large_vals) == [125, 163, 169]:
            if check_mwgp_same(163, d):
                print("d = {} is good".format(d))
