"""Représentation graphique d'une solution."""
import matplotlib.pyplot as plt

from src.utils import duree_tournee, profit_tournee

COULEURS = ["blue", "orange", "green", "purple", "brown",
            "deeppink", "gray", "olive", "cyan", "magenta"]


def tracer_solution(coords, P, D, L, tournees, d, a, titre="Tournées", fichier=None, afficher=True):
    """
    - départ d : carré vert, arrivée a : losange rouge
    - clients : points dont la taille dépend du profit, numérotés 1..n
      (même numérotation que l'affichage console)
    - une couleur par véhicule, légende = profit et durée
    - fichier : chemin d'une image à sauvegarder (optionnel)
    """
    n = len(P)
    plt.figure(figsize=(10, 8))
    plt.title(titre, fontsize=14)

    pmax = max(P) if P and max(P) > 0 else 1
    visites = {c for t in tournees for c in t}
    for c in range(n):
        taille = 30 + 120 * P[c] / pmax
        couleur = "steelblue" if c in visites else "lightgray"
        plt.scatter(*coords[c], s=taille, c=couleur, zorder=2)
        plt.annotate(str(c + 1), coords[c], textcoords="offset points",
                     xytext=(4, 4), fontsize=8)

    plt.scatter(*coords[d], c="green", s=200, marker="s", zorder=3, label="Départ (d)")
    plt.scatter(*coords[a], c="red", s=200, marker="D", zorder=3, label="Arrivée (a)")

    for k, t in enumerate(tournees):
        if not t:
            continue
        chemin = [d] + t + [a]
        xs = [coords[i][0] for i in chemin]
        ys = [coords[i][1] for i in chemin]
        plt.plot(xs, ys, color=COULEURS[k % len(COULEURS)], linewidth=2, zorder=1,
                 label=f"V{k+1} : profit {profit_tournee(P, t):.0f}, "
                       f"durée {duree_tournee(D, t, d, a):.1f}/{L}")

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.tight_layout()
    if fichier:
        plt.savefig(fichier, dpi=150)
    if afficher:
        plt.show()
    plt.close()