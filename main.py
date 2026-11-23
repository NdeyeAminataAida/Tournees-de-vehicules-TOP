"""Point d’entrée du programme de résolution du TOP."""
import copy
import time
from pathlib import Path

from src.utils import charger_instance, solution_valide
from src.utils import profit_total, duree_totale
from src.construction import (construction_gloutonne_sequentielle,
                              construction_gloutonne_parallele)
from src.optimisations import optimiser_2opt, optimiser_globale
from src.visualisation import tracer_solution
from src.affichage import (entete_instance, tableau_etapes, tableau_temps,
                           detail_meilleure_solution, resume_instance, bilan_global)

# ----------------------------------------------------------------------------
# Paramètres globaux
# ----------------------------------------------------------------------------
DOSSIER_INSTANCES = Path(__file__).parent / "instances"
DOSSIER_RESULTATS = Path(__file__).parent / "resultats"
AFFICHER_GRAPHIQUE = False        # False : seulement sauvegarder les images

instances = [
    "p1.2.k.txt",
    "p7.4.q.txt",
]

MODE_AFFICHAGE = "detail"  # "resume" ou "detail"

methodes = {
    "Séquentiel": construction_gloutonne_sequentielle,
    "Parallèle": construction_gloutonne_parallele,
}

criteres = ["ratio", "proche", "profit"]

# ----------------------------------------------------------------------------
# Programme principal
# ----------------------------------------------------------------------------
bilan_instances = []
for fichier in instances:
    chemin = DOSSIER_INSTANCES / fichier
    if not chemin.exists():
        print(f"\n[!] Instance introuvable, ignorée : {chemin}")
        continue

    n, m, L, P, D, coords = charger_instance(chemin)
    d, a = n, n + 1
    if MODE_AFFICHAGE == "detail":
        entete_instance(fichier, n, m, L, P, D, d, a)

    resultats = []
    for nom, methode in methodes.items():
        for critere in criteres:
            # Étape 1 : glouton
            t0 = time.perf_counter()
            sol_glouton = methode(D, P, L, m, n, d, a, critere=critere)
            t1 = time.perf_counter()

            # Étape 2 : 2-Opt (avec réinsertion des clients libres)
            sol_2opt = copy.deepcopy(sol_glouton)
            optimiser_2opt(D, P, L, sol_2opt, n, d, a, critere=critere)
            t2 = time.perf_counter()

            # Étape 3 : boucle globale (2-Opt, insertion, relocation, réinsertion)
            sol_global = copy.deepcopy(sol_2opt)
            optimiser_globale(D, P, L, sol_global, n, d, a, critere=critere)
            t3 = time.perf_counter()

            for sol in (sol_glouton, sol_2opt, sol_global):
                if not solution_valide(D, L, m, d, a, sol, n):
                    raise ValueError(f"Solution invalide : {fichier} / {nom} / {critere}")

            resultats.append({
                "nom": nom, "critere": critere,
                "clients": sum(len(t) for t in sol_global),
                "p_glouton": profit_total(P, sol_glouton), "d_glouton": duree_totale(D, sol_glouton, d, a),
                "p_2opt": profit_total(P, sol_2opt),       "d_2opt": duree_totale(D, sol_2opt, d, a),
                "p_global": profit_total(P, sol_global),   "d_global": duree_totale(D, sol_global, d, a),
                "t_glouton": t1 - t0, "t_2opt": t2 - t1, "t_global": t3 - t2,
                "sol_glouton": sol_glouton, "sol_2opt": sol_2opt, "sol_global": sol_global,
            })

    # Meilleure configuration : profit maximal, puis durée totale minimale
    i_meilleur = max(range(len(resultats)),
                     key=lambda i: (resultats[i]["p_global"], -resultats[i]["d_global"]))
    meilleur = resultats[i_meilleur]

    if MODE_AFFICHAGE == "detail":
        tableau_etapes(resultats, i_meilleur)
        tableau_temps(resultats)
        detail_meilleure_solution(meilleur, P, D, L, n, d, a)
    elif MODE_AFFICHAGE == "resume":
        resume_instance(fichier, n, m, L, meilleur)
    else:
        raise ValueError("MODE_AFFICHAGE doit être 'resume' ou 'detail'")

    bilan_instances.append((fichier, meilleur))

    DOSSIER_RESULTATS.mkdir(exist_ok=True)
    tracer_solution(coords, P, D, L, meilleur["sol_global"], d, a,
                    titre=f"{fichier} - {meilleur['nom']} / {meilleur['critere']} "
                          f"- profit {meilleur['p_global']:.0f}",
                    fichier=DOSSIER_RESULTATS / f"{Path(fichier).stem}.png",
                    afficher=AFFICHER_GRAPHIQUE)

if MODE_AFFICHAGE == "resume" and bilan_instances:
    bilan_global(bilan_instances)
