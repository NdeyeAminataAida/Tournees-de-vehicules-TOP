"""
Fonctions pour le Team Orienteering Problem (TOP).

Aucune variable globale ici : toutes les fonctions reçoivent leurs données en
paramètres (elles sont définies dans main.py).

Convention de numérotation :
    clients  : 0 .. n-1
    départ d : n
    arrivée a : n+1
Une tournée est une liste de clients (sans d ni a). Une solution est une liste
de m tournées (certaines peuvent être vides = véhicule inutilisé).
"""
import math


# ----------------------------------------------------------------------------
# Lecture de l'instance
# ----------------------------------------------------------------------------
def charger_instance(chemin):
    """
    Lit un fichier au format :
        n;<nb de sommets, départ et arrivée compris>
        m;<nb véhicules>
        tmax;<durée limite>
        x;y;profit        (1re ligne = départ d)
        ...               (n lignes clients)
        x;y;profit        (dernière ligne = arrivée a)

    Retourne (n, m, L, P, D) avec n = nombre de CLIENTS (= n_fichier - 2) :
        P[i] = profit du client i
        D = matrice des temps de trajet (distances euclidiennes),
               de taille (n+2) x (n+2), d = n et a = n+1.
    """
    with open(chemin, encoding="utf-8") as f:
        lignes = [l.strip() for l in f if l.strip()]

    n_sommets = int((lignes[0].split(";")[1]))
    m = int((lignes[1].split(";")[1]))
    L = float(lignes[2].split(";")[1])
    pts = [tuple(float(v) for v in l.split(";")) for l in lignes[3:]]

    if len(pts) != n_sommets:
        raise ValueError(f"{chemin} : {len(pts)} points lus, {n_sommets} annoncés")
    n = n_sommets - 2

    clients = pts[1:-1]
    P = [p for _, _, p in clients]
    coords = [(x, y) for x, y, _ in clients] + [pts[0][:2], pts[-1][:2]]
    D = [[math.dist(u, v) for v in coords] for u in coords]
    return n, m, L, P, D


# ----------------------------------------------------------------------------
# Évaluation d'une solution
# ----------------------------------------------------------------------------
def duree_tournee(D, tournee, d, a):
    """Durée d -> clients -> a. Une tournée vide a une durée nulle."""
    if not tournee:
        return 0.0
    t = D[d][tournee[0]] + D[tournee[-1]][a]
    for i in range(len(tournee) - 1):
        t += D[tournee[i]][tournee[i + 1]]
    return t


def profit_total(P, tournees):
    return sum(P[c] for t in tournees for c in t)


def duree_totale(D, tournees, d, a):
    return sum(duree_tournee(D, t, d, a) for t in tournees)


def solution_valide(D, L, m, d, a, tournees, n):
    """Vérifie : <= m tournées, durée <= L, clients dans [0,n-1], aucun doublon."""
    if len(tournees) > m:
        return False
    vus = set()
    for t in tournees:
        if duree_tournee(D, t, d, a) > L + 1e-9:
            return False
        for c in t:
            if not (0 <= c < n) or c in vus:
                return False
            vus.add(c)
    return True


# ----------------------------------------------------------------------------
# Insertion d'un client
# ----------------------------------------------------------------------------
def surcout_insertion(D, tournee, pos, j, d, a):
    """Variation de durée en insérant j à la position pos : Dij + Djk - Dik."""
    if not tournee:
        return D[d][j] + D[j][a]
    prec = d if pos == 0 else tournee[pos - 1]
    suiv = a if pos == len(tournee) else tournee[pos]
    return D[prec][j] + D[j][suiv] - D[prec][suiv]


def _score(critere, profit, surcout):
    if critere == "ratio":       # profit par unité de temps ajoutée
        return profit / (surcout + 1e-9)
    if critere == "proche":      # variation minimale (PPI du cours)
        return -surcout
    if critere == "profit":      # plus gros profit d'abord (PLI/glouton)
        return profit * 1e6 - surcout
    raise ValueError(f"critère inconnu : {critere}")


def _meilleure_insertion(D, P, L, tournees, durees, libres, d, a, critere):
    """Meilleure insertion faisable (client, tournée, position) ou None."""
    meilleure = None
    for j in libres:
        for k, t in enumerate(tournees):
            for pos in range(len(t) + 1):
                ds = surcout_insertion(D, t, pos, j, d, a)
                if durees[k] + ds <= L + 1e-9:
                    sc = _score(critere, P[j], ds)
                    if meilleure is None or sc > meilleure[0]:
                        meilleure = (sc, j, k, pos, ds)
    return meilleure

# ----------------------------------------------------------------------------
# 1. Algorithme glouton : insertion séquentielle
# ----------------------------------------------------------------------------
def construction_gloutonne_sequentielle(D, P, L, m, n, d, a, critere="ratio"):
    tournees = [[] for _ in range(m)]
    durees = [0.0] * m
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

# ----------------------------------------------------------------------------
# 2. Algorithme glouton : insertion parallèle
# ----------------------------------------------------------------------------
def construction_gloutonne_parallele(D, P, L, m, n, d, a, critere="ratio"):
    """
    Part de m tournées vides. À chaque étape, on évalue toutes les insertions
    faisables (client libre j, tournée k, position p) et on exécute la meilleure
    selon le critère ('ratio', 'proche' ou 'profit'). On s'arrête quand plus
    aucun client ne peut être inséré sans dépasser L.
    """
    tournees = [[] for _ in range(m)]
    durees = [0.0] * m
    libres = set(range(n))
    while libres:
        best = _meilleure_insertion(D, P, L, tournees, durees, libres, d, a, critere)
        if best is None:
            break
        _, j, k, pos, ds = best
        tournees[k].insert(pos, j)
        durees[k] += ds
        libres.remove(j)
    return tournees


# ----------------------------------------------------------------------------
# 3. Optimisation 2-Opt
# ----------------------------------------------------------------------------
def deux_opt(D, tournee, d, a):
    """
    2-Opt sur une tournée (modifiée en place). On parcourt le chemin
    d -> c1 -> ... -> ck -> a et on inverse une section dès que
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


def inserer_libres(D, P, L, tournees, n, d, a, critere="ratio"):
    """Insère tous les clients libres encore faisables. Retourne True si au moins un."""
    present = {c for t in tournees for c in t}
    libres = {j for j in range(n) if j not in present}
    durees = [duree_tournee(D, t, d, a) for t in tournees]
    insere = False
    while libres:
        best = _meilleure_insertion(D, P, L, tournees, durees, libres, d, a, critere)
        if best is None:
            break
        _, j, k, pos, ds = best
        tournees[k].insert(pos, j)
        durees[k] += ds
        libres.remove(j)
        insere = True
    return insere


def optimiser_2opt(D, P, L, tournees, n, d, a, critere="ratio"):
    """
    Alterne 2-Opt (raccourcit chaque tournée) et réinsertion des clients libres
    (le temps gagné permet d'en servir de nouveaux) jusqu'à stabilité.
    Retourne le nombre de tours effectués.
    """
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
