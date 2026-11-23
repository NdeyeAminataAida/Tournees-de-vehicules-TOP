"""
Améliorations d'une solution (modifiée en place) :
  - deux_opt / optimiser_2opt : raccourcir chaque tournée
  - inserer_libres            : utiliser le temps gagné pour servir de nouveaux clients
  - relocaliser               : déplacer un client d'une tournée à une autre
  - optimiser_globale         : enchaîne le tout jusqu'à stabilité
"""
from src.utils import (duree_tournee, duree_totale, profit_total, surcout_insertion)
from src.construction import meilleure_insertion


# ----------------------------------------------------------------------------
# 1. 2-Opt (intra-tournée)
# ----------------------------------------------------------------------------
def deux_opt(D, tournee, d, a):
    """
    2-Opt sur une tournée (modifiée en place). On inverse une section dès que
        D[i][j] + D[i+1][j+1] < D[i][i+1] + D[j][j+1].
    d et a restent aux extrémités. Retourne True si la tournée a été raccourcie.
    """
    chemin = [d] + tournee + [a]
    amelioree = False
    ameliore = True
    while ameliore:
        ameliore = False
        for i in range(len(chemin) - 3):
            for j in range(i + 2, len(chemin) - 1):
                delta = (D[chemin[i]][chemin[j]] + D[chemin[i + 1]][chemin[j + 1]]
                         - D[chemin[i]][chemin[i + 1]] - D[chemin[j]][chemin[j + 1]])
                if delta < -1e-9:
                    chemin[i + 1:j + 1] = reversed(chemin[i + 1:j + 1])
                    ameliore = amelioree = True
    tournee[:] = chemin[1:-1]
    return amelioree


# ----------------------------------------------------------------------------
# 2. Insertion des clients libres
# ----------------------------------------------------------------------------
def inserer_libres(D, P, L, tournees, n, d, a, critere="ratio"):
    """Insère tous les clients libres encore faisables. Retourne True si au moins un."""
    present = {c for t in tournees for c in t}
    libres = {j for j in range(n) if j not in present}
    durees = [duree_tournee(D, t, d, a) for t in tournees]
    insere = False
    while libres:
        best = meilleure_insertion(D, P, L, tournees, durees, libres, d, a, critere)
        if best is None:
            break
        _, j, k, pos, ds = best
        tournees[k].insert(pos, j)
        durees[k] += ds
        libres.remove(j)
        insere = True
    return insere


def optimiser_2opt(D, P, L, tournees, n, d, a, critere="ratio"):
    """Alterne 2-Opt et réinsertion des clients libres jusqu'à stabilité."""
    tours = 0
    while True:
        tours += 1
        raccourci = False
        for t in tournees:
            if len(t) >= 2 and deux_opt(D, t, d, a):
                raccourci = True
        insere = inserer_libres(D, P, L, tournees, n, d, a, critere)
        if not (raccourci or insere):
            return tours


# ----------------------------------------------------------------------------
# 3. Relocation (inter-tournées)
# ----------------------------------------------------------------------------
def relocaliser(D, L, tournees, d, a):
    """
    Applique le déplacement d'un client (tournée k1 -> tournée k2) qui réduit le
    plus  (durée totale) + 2 x (durée max). Le profit ne change pas, mais du
    temps est libéré pour insérer ensuite de nouveaux clients.
    Retourne True si un déplacement a été appliqué.
    """
    m = len(tournees)
    durees = [duree_tournee(D, t, d, a) for t in tournees]
    total, maxi = sum(durees), max(durees)
    meilleur, meilleur_score = None, 1e-9

    for k1, t1 in enumerate(tournees):
        for idx, c in enumerate(t1):
            nouv1 = duree_tournee(D, t1[:idx] + t1[idx + 1:], d, a)
            for k2 in range(m):
                if k2 == k1:
                    continue
                t2 = tournees[k2]
                for pos in range(len(t2) + 1):
                    nouv2 = durees[k2] + surcout_insertion(D, t2, pos, c, d, a)
                    if nouv2 > L + 1e-9:
                        continue
                    nouveau_total = total - durees[k1] - durees[k2] + nouv1 + nouv2
                    nouveau_max = max([nouv1, nouv2] +
                                      [durees[x] for x in range(m) if x not in (k1, k2)])
                    score = (total - nouveau_total) + 2.0 * (maxi - nouveau_max)
                    if score > meilleur_score:
                        meilleur_score = score
                        meilleur = (k1, idx, k2, pos)

    if meilleur is None:
        return False
    k1, idx, k2, pos = meilleur
    c = tournees[k1].pop(idx)
    tournees[k2].insert(pos, c)
    return True


# ----------------------------------------------------------------------------
# 4. Boucle globale
# ----------------------------------------------------------------------------
def optimiser_globale(D, P, L, tournees, n, d, a, critere="ratio",
                      max_tours=12, verbose=False):
    """
    Répète : 2-Opt -> insertion des libres -> relocations -> insertion des libres
    (le temps libéré par les relocations est utilisé tout de suite).
    S'arrête quand ni le profit n'augmente, ni la durée totale ne diminue,
    ou après max_tours. Retourne le nombre de tours effectués.
    """
    def etat():
        return profit_total(P, tournees), duree_totale(D, tournees, d, a)

    for tour in range(1, max_tours + 1):
        profit_avant, duree_avant = etat()
        if verbose:
            print(f"\n--- Tour {tour} ---")

        for t in tournees:
            if len(t) >= 2:
                deux_opt(D, t, d, a)
        if verbose:
            print(f"Profit après 2-opt        : {profit_total(P, tournees):.0f}")

        inserer_libres(D, P, L, tournees, n, d, a, critere)
        if verbose:
            print(f"Profit après insertion    : {profit_total(P, tournees):.0f}")

        while relocaliser(D, L, tournees, d, a):
            pass
        if verbose:
            print(f"Durée totale après reloc. : {duree_totale(D, tournees, d, a):.2f}")

        inserer_libres(D, P, L, tournees, n, d, a, critere)
        profit_apres, duree_apres = etat()
        if verbose:
            print(f"Profit fin de tour        : {profit_apres:.0f}")

        if not (profit_apres > profit_avant + 1e-9 or
                (abs(profit_apres - profit_avant) <= 1e-9 and duree_apres < duree_avant - 1e-9)):
            return tour
    return max_tours