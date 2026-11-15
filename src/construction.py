"""Constructions gloutonnes d'une solution initiale (séquentielle et parallèle)."""
from src.utils import surcout_insertion


def _score(critere, profit, surcout):
    if critere == "ratio":       # profit par unité de temps ajoutée
        return profit / (surcout + 1e-9)
    if critere == "proche":      # variation minimale (PPI du cours)
        return -surcout
    if critere == "profit":      # plus gros profit d'abord
        return profit * 1e6 - surcout
    raise ValueError(f"critère inconnu : {critere}")


def meilleure_insertion(D, P, L, tournees, durees, libres, d, a, critere):
    """Meilleure insertion faisable (score, client, tournée, position, surcoût) ou None."""
    meilleure = None
    for j in sorted(libres):
        for k, t in enumerate(tournees):
            for pos in range(len(t) + 1):
                ds = surcout_insertion(D, t, pos, j, d, a)
                if durees[k] + ds <= L + 1e-9:
                    sc = _score(critere, P[j], ds)
                    if meilleure is None or sc > meilleure[0]:
                        meilleure = (sc, j, k, pos, ds)
    return meilleure


def construction_gloutonne_sequentielle(D, P, L, m, n, d, a, critere="ratio"):
    """Remplit le véhicule 1 au maximum, puis le 2, etc."""
    tournees = [[] for _ in range(m)]
    durees = [D[d][a]] * m
    libres = set(range(n))

    for k in range(m):
        while libres:
            meilleure = None
            for j in sorted(libres):
                for pos in range(len(tournees[k]) + 1):
                    ds = surcout_insertion(D, tournees[k], pos, j, d, a)
                    if durees[k] + ds <= L + 1e-9:
                        sc = _score(critere, P[j], ds)
                        if meilleure is None or sc > meilleure[0]:
                            meilleure = (sc, j, pos, ds)
            if meilleure is None:
                break
            _, j, pos, ds = meilleure
            tournees[k].insert(pos, j)
            durees[k] += ds
            libres.remove(j)
    return tournees


def construction_gloutonne_parallele(D, P, L, m, n, d, a, critere="ratio"):
    """À chaque étape, exécute la meilleure insertion (client, tournée, position)."""
    tournees = [[] for _ in range(m)]
    durees = [D[d][a]] * m
    libres = set(range(n))
    while libres:
        best = meilleure_insertion(D, P, L, tournees, durees, libres, d, a, critere)
        if best is None:
            break
        _, j, k, pos, ds = best
        tournees[k].insert(pos, j)
        durees[k] += ds
        libres.remove(j)
    return tournees