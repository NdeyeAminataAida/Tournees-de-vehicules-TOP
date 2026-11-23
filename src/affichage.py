"""
Affichage console des résultats : tableaux comparatifs et détail de la meilleure solution.

Aucune donnée globale ici : tout est passé en paramètres depuis main.py.
Un "résultat" est un dictionnaire décrivant une configuration (méthode + critère) :
    nom, critere, clients,
    p_glouton, d_glouton, p_2opt, d_2opt, p_global, d_global     (profits et durées totales)
    t_glouton, t_2opt, t_global                                  (temps de calcul, en secondes)
    sol_glouton, sol_2opt, sol_global                            (tournées à chaque étape)
"""
import textwrap

from src.utils import duree_tournee, profit_tournee

LARGEUR = 100


def _ligne(car="="):
    print(car * LARGEUR)


def entete_instance(fichier, n, m, L, P, D, d, a):
    """Bandeau de présentation d'une instance."""
    print()
    _ligne("=")
    print(f"INSTANCE {fichier}")
    _ligne("=")
    print(f"  Clients : {n}    Véhicules : {m}    Durée maximale L : {L:g}")
    print(f"  Profit total disponible : {sum(P):.0f}    "
          f"Durée du trajet direct d -> a : {D[d][a]:.2f}")


def tableau_etapes(resultats, i_meilleur):
    """Profit et durée totale des tournées à chaque étape, pour chaque configuration."""
    print("\nProfit et durée totale des tournées à chaque étape")
    _ligne("-")
    print(f"{'':<11} {'':<7} | {'Glouton':^16} | {'+ 2-Opt':^16} | {'+ Global':^16} | "
          f"{'Clients':>7} | {'Gain':>6}")
    print(f"{'Méthode':<11} {'Critère':<7} | {'Profit':>6} {'Durée':>9} | {'Profit':>6} {'Durée':>9} | "
          f"{'Profit':>6} {'Durée':>9} | {'servis':>7} | {'profit':>6}")
    _ligne("-")
    for i, r in enumerate(resultats):
        gain = r["p_global"] - r["p_glouton"]
        marque = "  <- meilleure" if i == i_meilleur else ""
        print(f"{r['nom']:<11} {r['critere']:<7} | "
              f"{r['p_glouton']:>6.0f} {r['d_glouton']:>9.2f} | "
              f"{r['p_2opt']:>6.0f} {r['d_2opt']:>9.2f} | "
              f"{r['p_global']:>6.0f} {r['d_global']:>9.2f} | "
              f"{r['clients']:>7} | {gain:>+6.0f}{marque}")
    _ligne("-")


def tableau_temps(resultats):
    """Temps de calcul de chaque étape (en millisecondes)."""
    print("\nTemps de calcul par étape (ms)")
    _ligne("-")
    print(f"{'Méthode':<11} {'Critère':<7} | {'Glouton':>9} {'2-Opt':>9} {'Global':>9} | {'Total':>9}")
    _ligne("-")
    for r in resultats:
        tg, t2, tl = r["t_glouton"] * 1000, r["t_2opt"] * 1000, r["t_global"] * 1000
        print(f"{r['nom']:<11} {r['critere']:<7} | {tg:>9.2f} {t2:>9.2f} {tl:>9.2f} | {tg + t2 + tl:>9.2f}")
    _ligne("-")


def detail_meilleure_solution(resultat, P, D, L, n, d, a):
    """Détail de la meilleure solution : durées par véhicule à chaque étape, tournées finales."""
    r = resultat
    final = r["sol_global"]
    visites = {c for t in final for c in t}

    print(f"\nMEILLEURE SOLUTION : {r['nom']} / critère '{r['critere']}'")
    _ligne("-")
    gain = r["p_global"] - r["p_glouton"]
    pct = 100 * gain / r["p_glouton"] if r["p_glouton"] else 0
    print(f"  Profit : {r['p_glouton']:.0f} (glouton) -> {r['p_2opt']:.0f} (+ 2-Opt) "
          f"-> {r['p_global']:.0f} (+ Global)    gain {gain:+.0f} ({pct:+.1f} %)")
    print(f"  Durée totale : {r['d_glouton']:.2f} -> {r['d_2opt']:.2f} -> {r['d_global']:.2f}")
    print(f"  Clients servis : {len(visites)} sur {n}")

    print("\n  Durée de chaque véhicule à chaque étape (limite L = "
          f"{L:g})")
    print(f"  {'Véh.':>4} | {'Clients':>7} {'Profit':>7} | {'Glouton':>9} {'+ 2-Opt':>9} {'+ Global':>9} | "
          f"{'Marge':>7}")
    for k, t in enumerate(final):
        dg = duree_tournee(D, r["sol_glouton"][k], d, a)
        d2 = duree_tournee(D, r["sol_2opt"][k], d, a)
        df = duree_tournee(D, t, d, a)
        print(f"  {k + 1:>4} | {len(t):>7} {profit_tournee(P, t):>7.0f} | "
              f"{dg:>9.2f} {d2:>9.2f} {df:>9.2f} | {L - df:>7.2f}")

    print("\n  Tournées finales")
    for k, t in enumerate(final, start=1):
        parcours = " -> ".join(["d"] + [str(c + 1) for c in t] + ["a"])
        entete = f"  V{k} : "
        print(textwrap.fill(parcours, width=LARGEUR, initial_indent=entete,
                            subsequent_indent=" " * len(entete)))

    non_visites = [c + 1 for c in sorted(set(range(n)) - visites)]
    print()
    if non_visites:
        entete = f"  Clients non visités ({len(non_visites)}) : "
        print(textwrap.fill(", ".join(map(str, non_visites)), width=LARGEUR,
                            initial_indent=entete, subsequent_indent=" " * 4))
    else:
        print("  Tous les clients sont visités.")


def resume_instance(fichier, n, m, L, r):
    """Une synthèse courte de la meilleure configuration pour une instance."""
    gain = r["p_global"] - r["p_glouton"]
    pourcentage = 100 * gain / r["p_glouton"] if r["p_glouton"] else 0
    temps_ms = 1000 * (r["t_glouton"] + r["t_2opt"] + r["t_global"])
    print("\n" + "=" * 60)
    print(f"INSTANCE {fichier} | {n} clients | {m} véhicules | L={L:g}")
    print("=" * 60)
    print(f"Meilleure configuration : {r['nom']} / {r['critere']}")
    print(f"{'':19} {'Glouton':>10} {'2-Opt':>10} {'Global':>10}")
    print(f"{'Profit':19} {r['p_glouton']:>10.0f} {r['p_2opt']:>10.0f} {r['p_global']:>10.0f}")
    print(f"{'Durée totale':19} {r['d_glouton']:>10.2f} {r['d_2opt']:>10.2f} {r['d_global']:>10.2f}")
    print(f"Gain de profit : {gain:+.0f} ({pourcentage:+.1f} %) | "
          f"Clients servis : {r['clients']}/{n} | Temps : {temps_ms:.2f} ms")


def bilan_global(bilan_instances):
    """Une seule ligne par instance pour faciliter les exécutions en série."""
    print("\n" + "=" * 83)
    print("BILAN GLOBAL DES INSTANCES")
    print("=" * 83)
    print(f"{'Instance':<15} {'Méthode':<12} {'Critère':<8} "
          f"{'Profit G':>9} {'Profit F':>9} {'Durée F':>9} {'Temps ms':>9}")
    print("-" * 83)
    for fichier, r in bilan_instances:
        total_ms = 1000 * (r["t_glouton"] + r["t_2opt"] + r["t_global"])
        print(f"{fichier:<15} {r['nom']:<12} {r['critere']:<8} "
              f"{r['p_glouton']:>9.0f} {r['p_global']:>9.0f} "
              f"{r['d_global']:>9.2f} {total_ms:>9.2f}")
