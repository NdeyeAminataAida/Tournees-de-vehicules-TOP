import copy
import time
from pathlib import Path

from src.utils import (charger_instance, profit_total, profit_tournee, duree_totale,
                       duree_tournee, solution_valide)
from src.construction import (construction_gloutonne_sequentielle,
                              construction_gloutonne_parallele)
from src.optimisations import optimiser_2opt, optimiser_globale
from src.visualisation import tracer_solution

DOSSIER_INSTANCES = Path(__file__).parent / "instances"
DOSSIER_RESULTATS = Path(__file__).parent / "resultats"
AFFICHER_GRAPHIQUE = True        # False : seulement sauvegarder les images

instances = [
    "p7.4.r.txt",
    "p7.4.q.txt",
]

methodes = {
    "Séquentiel": construction_gloutonne_sequentielle,
    "Parallèle": construction_gloutonne_parallele,
}

criteres = ["ratio", "proche", "profit"]


for fichier in instances:
    n, m, L, P, D, coords = charger_instance(DOSSIER_INSTANCES / fichier)
    d, a = n, n + 1

    print("\n" + "=" * 100)
    print(f"{fichier} : n = {n}, m = {m}, L = {L}, Profit total disponible : {sum(P):.0f}")
    print("=" * 100)
    print(f"{'Méthode':<13} {'Critère':<9} {'Glouton':>9} {'+ 2-Opt':>9} "
          f"{'+ Global':>9} {'Durée':>9} {'Clients':>8} {'Temps(s)':>9}")

    meilleur = None   # (profit, -durée, nom, critère, tournées)

    for nom, methode in methodes.items():
        for critere in criteres:
            debut = time.perf_counter()

            tournees = methode(D, P, L, m, n, d, a, critere=critere)
            p_glouton = profit_total(P, tournees)

            optimiser_2opt(D, P, L, tournees, n, d, a, critere=critere)
            p_2opt = profit_total(P, tournees)

            optimiser_globale(D, P, L, tournees, n, d, a, critere=critere)
            p_final = profit_total(P, tournees)
            duree_finale = duree_totale(D, tournees, d, a)
            nb_clients = sum(len(t) for t in tournees)

            temps = time.perf_counter() - debut
            assert solution_valide(D, L, m, d, a, tournees, n), "Solution non valide !"

            print(f"{nom:<13} {critere:<9} {p_glouton:>9.0f} {p_2opt:>9.0f} "
                  f"{p_final:>9.0f} {duree_finale:>9.2f} {nb_clients:>8} {temps:>9.4f}")

            cle = (p_final, -duree_finale)
            if meilleur is None or cle > meilleur[0]:
                meilleur = (cle, nom, critere, copy.deepcopy(tournees))

    (profit_best, _), nom, critere, tournees = meilleur
    print(f"\nMeilleure solution : {nom}, critère '{critere}', "
          f"profit total collecté = {profit_best:.0f}")

    for k, t in enumerate(tournees, start=1):
        parcours = " -> ".join(["d"] + [str(c + 1) for c in t] + ["a"])
        print(f"Véhicule {k} : {parcours} "
              f"(profit {profit_tournee(P, t):.0f}, durée {duree_tournee(D, t, d, a):.2f} / {L})")

    visites = {c for t in tournees for c in t}
    non_visites = sorted(set(range(n)) - visites)
    print(f"\nClients non visités ({len(non_visites)}) : {[c + 1 for c in non_visites]}")

    DOSSIER_RESULTATS.mkdir(exist_ok=True)
    tracer_solution(coords, P, D, L, tournees, d, a,
                    titre=f"{fichier} - {nom} / {critere} - profit {profit_best:.0f}",
                    fichier=DOSSIER_RESULTATS / f"{Path(fichier).stem}.png",
                    afficher=AFFICHER_GRAPHIQUE)