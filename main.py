
import time
from pathlib import Path

DOSSIER_INSTANCES = Path(__file__).parent / "instances"

from src.tournees import (
    charger_instance,
    construction_gloutonne_sequentielle,
    construction_gloutonne_parallele,
    optimiser_2opt,
    profit_total,
    duree_totale,
    duree_tournee,
    solution_valide,
)

instances = [
    "p1.2.k.txt",
    "p7.4.q.txt",
]

methodes = {
    "Séquentiel": construction_gloutonne_sequentielle,
    "Parallèle": construction_gloutonne_parallele,
}

criteres = ["ratio", "proche", "profit"]


for fichier in instances:
    n, m, L, P, D = charger_instance(DOSSIER_INSTANCES / fichier)
    d, a = n, n + 1
    profit_disponible = sum(P)

    print("\n" + "=" * 100)
    print(f"{fichier} : n = {n}, m = {m}, L = {L}, Profit total disponible : {profit_disponible}")
    print("=" * 100)

    print(
        f"{'Méthode':<13} {'Critère':<9} "
        f"{'Glouton':>9} {'Durée':>9} "
        f"{'+ 2-Opt':>9} {'Durée':>9} "
        f"{'Clients':>8} {'Temps exécution(s)':>11}"
    
    )

    meilleure_solution = None
    meilleur_profit = -1

    for nom, methode in methodes.items():
        for critere in criteres:
            debut = time.perf_counter()

            tournees = methode(
                D, P, L, m, n, d, a, critere=critere
            )

            profit_initial = profit_total(P, tournees)
            duree_initiale = duree_totale(D, tournees, d, a)

            optimiser_2opt(
                D, P, L, tournees, n, d, a, critere=critere
            )

            profit_final = profit_total(P, tournees)
            duree_finale = duree_totale(D, tournees, d, a)
            nb_clients = sum(len(t) for t in tournees)

            temps = time.perf_counter() - debut

            assert solution_valide(
                D, L, m, d, a, tournees, n
            ), "Solution non valide !"

            print(
                f"{nom:<13} {critere:<9} "
                f"{profit_initial:>9.0f} {duree_initiale:>9.2f} "
                f"{profit_final:>9.0f} {duree_finale:>9.2f} "
                f"{nb_clients:>8} {temps:>11.4f}"
            )

            if profit_final > meilleur_profit:
                meilleur_profit = profit_final
                meilleure_solution = (
                    nom,
                    critere,
                    [t.copy() for t in tournees]
                )

    nom, critere, tournees = meilleure_solution

    print(
        f"\nMeilleure solution : {nom}, "
        f"critère '{critere}', profit total collecté = {meilleur_profit:.0f}"
    )
    

    for k, tournee in enumerate(tournees, start=1):
        parcours = " -> ".join(
            ["d"] + [str(c + 1) for c in tournee] + ["a"]
        )

        duree = duree_tournee(D, tournee, d, a)

        print(
            f"Véhicule {k} : {parcours} "
            f"(durée {duree:.2f} / {L})"
        )
    
    # Clients non visités
    clients_visites = {c for tournee in tournees for c in tournee}
    clients_non_visites = sorted(set(range(n)) - clients_visites)

    print(
        f"\nClients non visités ({len(clients_non_visites)}) : "
        f"{[c + 1 for c in clients_non_visites]}"
    )