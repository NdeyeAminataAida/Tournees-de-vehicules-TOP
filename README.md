# Tournées de véhicules : Team Orienteering Problem (TOP)

Heuristiques de résolution du **Team Orienteering Problem** : une flotte de `m` véhicules part d'un dépôt de départ `d`, termine à un dépôt d'arrivée `a`, et dispose chacun d'une durée maximale `L`. Chaque client a un profit, collecté une seule fois. L'objectif est de **maximiser le profit total collecté**.

## Structure du projet

```
.
├── main.py                 # point d'entrée : compare toutes les méthodes
├── instances/              # fichiers d'instances (.txt)
├── resultats/              # images générées (créé automatiquement)
└── src/
    ├── __init__.py
    ├── utils.py            # lecture d'instance, durées, profits, validation
    ├── construction.py     # constructions gloutonnes
    ├── optimisations.py    # 2-opt, insertion, relocation, boucle globale
    └── visualisation.py    # graphique des tournées
```

## Installation

Python 3.8 ou plus récent est nécessaire. Seule la visualisation demande une bibliothèque externe :

```bash
pip install matplotlib
```

## Utilisation

1. Place les fichiers d'instances dans `instances/`.
2. Indique ceux à traiter dans la liste `instances` de `main.py` :
   ```python
   instances = ["p1.2.k.txt", "p7.4.q.txt"]
   ```
3. Lance le programme **depuis la racine du projet** (le dossier qui contient `main.py`) :
   ```bash
   python main.py
   ```

Pour sauvegarder les images sans ouvrir de fenêtre, mets `AFFICHER_GRAPHIQUE = False` dans `main.py`.

## Format d'une instance

Fichier texte, valeurs séparées par des `;`. La première ligne de points est le départ, la dernière est l'arrivée :

```
n;<nombre de sommets, départ et arrivée compris>
m;<nombre de véhicules>
tmax;<durée maximale d'une tournée>
x;y;profit        (départ d)
x;y;profit        (client 1)
...
x;y;profit        (arrivée a)
```

Les durées de trajet sont les distances euclidiennes. Une instance où `d -> a` dépasse déjà `tmax` est refusée.

## Convention de représentation

- Les clients sont numérotés `0 .. n-1`, le départ est `d = n` et l'arrivée `a = n+1`.
- Une **tournée** est une liste de clients, **sans** `d` ni `a` : les dépôts sont implicites, car chaque véhicule part de `d` et finit en `a`.
- Une **solution** est une liste de `m` tournées. Un véhicule inutilisé a la tournée vide `[]`, de durée `D[d][a]`.
- À l'affichage, les clients sont numérotés de 1 à n.

## Méthodes

### Construction d'une solution initiale (`construction.py`)

| Méthode | Principe |
|---|---|
| Séquentielle | Remplit le véhicule 1 au maximum, puis le 2, etc. |
| Parallèle | À chaque étape, exécute la meilleure insertion possible (client, tournée, position). |

Trois critères de choix de l'insertion, utilisables avec les deux méthodes :

- `ratio` : profit divisé par le surcoût en temps ;
- `proche` : surcoût en temps minimal ;
- `profit` : plus gros profit d'abord.

### Amélioration (`optimisations.py`)

- **2-opt** : inverse des sections d'une tournée pour la raccourcir.
- **Insertion des clients libres** : utilise le temps gagné pour servir de nouveaux clients.
- **Relocation** : déplace un client d'une tournée à une autre quand cela réduit la durée totale et la durée maximale, ce qui libère du temps pour de nouvelles insertions.
- **Boucle globale** (`optimiser_globale`) : répète 2-opt, insertion, relocation, puis une nouvelle insertion, jusqu'à ce que le profit n'augmente plus et que la durée totale ne diminue plus (12 tours maximum).

## Résultats affichés

Pour chaque instance, `main.py` affiche un tableau comparatif :

| Colonne | Signification |
|---|---|
| Glouton | profit après la construction seule |
| + 2-Opt | profit après 2-opt et réinsertion |
| + Global | profit après la boucle globale (avec relocation) |
| Durée | durée totale des tournées |
| Clients | nombre de clients servis |
| Temps(s) | temps d'exécution |

Il détaille ensuite la meilleure solution (tournées, profit et durée par véhicule, clients non visités) et enregistre un graphique dans `resultats/`. Chaque solution est vérifiée par `solution_valide` (au plus `m` tournées, durée maximale respectée, aucun client en double).

## Équipe

- NdeyeAminataAida
- MaxAllegri
