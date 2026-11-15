"""
Outils de base pour le Team Orienteering Problem (TOP).

Convention de numérotation :
    clients   : 0 .. n-1
    départ d  : n
    arrivée a : n+1
Une tournée est une liste de clients (SANS d ni a). Chaque véhicule part
OBLIGATOIREMENT de d et finit en a : une tournée vide [] vaut donc d -> a
(durée D[d][a]). Une solution est une liste de m tournées.
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
        ...               (clients)
        x;y;profit        (dernière ligne = arrivée a)

    Retourne (n, m, L, P, D, coords) avec n = nombre de CLIENTS :
        P[i]      = profit du client i
        D         = matrice des durées (distances euclidiennes), (n+2)x(n+2)
        coords[i] = (x, y) du sommet i (clients, puis d = n, puis a = n+1)
    """
    with open(chemin, encoding="utf-8") as f:
        lignes = [l.strip() for l in f if l.strip()]

    n_sommets = int(lignes[0].split(";")[1])
    m = int(lignes[1].split(";")[1])
    L = float(lignes[2].split(";")[1])
    pts = [tuple(float(v) for v in l.split(";")) for l in lignes[3:]]

    if len(pts) != n_sommets:
        raise ValueError(f"{chemin} : {len(pts)} points lus, {n_sommets} annoncés")
    n = n_sommets - 2

    clients = pts[1:-1]
    P = [p for _, _, p in clients]
    coords = [(x, y) for x, y, _ in clients] + [pts[0][:2], pts[-1][:2]]
    D = [[math.dist(u, v) for v in coords] for u in coords]

    if D[n][n + 1] > L + 1e-9:
        raise ValueError(f"{chemin} : d -> a dure {D[n][n+1]:.2f} > L = {L} (instance infaisable)")
    return n, m, L, P, D, coords


# ----------------------------------------------------------------------------
# Évaluation d'une solution
# ----------------------------------------------------------------------------
def duree_tournee(D, tournee, d, a):
    """Durée d -> clients -> a. Une tournée vide vaut d -> a."""
    if not tournee:
        return D[d][a]
    t = D[d][tournee[0]] + D[tournee[-1]][a]
    for i in range(len(tournee) - 1):
        t += D[tournee[i]][tournee[i + 1]]
    return t


def profit_tournee(P, tournee):
    return sum(P[c] for c in tournee)


def profit_total(P, tournees):
    return sum(P[c] for t in tournees for c in t)


def duree_totale(D, tournees, d, a):
    return sum(duree_tournee(D, t, d, a) for t in tournees)


def solution_valide(D, L, m, d, a, tournees, n):
    """Vérifie : <= m tournées, durée <= L, clients dans [0,n-1], aucun doublon."""
    if len(tournees) > m or D[d][a] > L + 1e-9:
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
    """
    Variation de durée en insérant j à la position pos : Dij + Djk - Dik.
    Pour une tournée vide, le trajet d -> a existe déjà : Ddj + Dja - Dda.
    """
    if not tournee:
        return D[d][j] + D[j][a] - D[d][a]
    prec = d if pos == 0 else tournee[pos - 1]
    suiv = a if pos == len(tournee) else tournee[pos]
    return D[prec][j] + D[j][suiv] - D[prec][suiv]