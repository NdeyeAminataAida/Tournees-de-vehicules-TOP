# Tournées de véhicules — Team Orienteering Problem (TOP)

Projet réalisé dans le cadre de l'UV **AI09 — Simulation et techniques d'optimisation**, à l'Université de Technologie de Compiègne (UTC).

L'objectif est de résoudre le **Team Orienteering Problem (TOP)** à l'aide d'heuristiques de construction et d'amélioration implémentées en Python.

## 1. Présentation du problème

Le TOP consiste à organiser les tournées d'une flotte de \(m\) véhicules, chacun partant d'un dépôt de départ `d` et rejoignant un dépôt d'arrivée `a`.

Chaque client possède un profit, collecté au plus une fois. Chaque véhicule dispose d'une durée maximale de parcours `L`.

L'objectif est de **maximiser le profit total collecté**, tout en respectant les contraintes de durée et d'unicité des visites.

## 2. Structure du projet

```text
.
├── main.py                 # Exécution et comparaison des méthodes
├── instances/              # Fichiers d'instances (.txt)
├── resultats/              # Graphiques générés
└── src/
    ├── __init__.py
    ├── utils.py            # Lecture, distances, profits, validation
    ├── construction.py     # Constructions gloutonnes
    ├── optimisations.py    # 2-Opt, insertion, relocation
    ├── affichage.py        # Affichage des résultats
    └── visualisation.py    # Visualisation des tournées
```

## 3. Installation

Le projet nécessite **Python 3.8 ou une version plus récente**.

Installer la bibliothèque utilisée pour la visualisation :

```bash
pip install matplotlib
```

Aucune autre bibliothèque externe n'est nécessaire.

## 4. Utilisation

Placer les fichiers d'instances dans le dossier `instances/`.

Dans `main.py`, définir les instances à traiter :

```python
instances = ["p1.2.k.txt", "p7.4.q.txt"]
```

Lancer ensuite le programme depuis la racine du projet :

```bash
python main.py
```

### Configuration de l'affichage

Deux modes sont disponibles :

```python
MODE_AFFICHAGE = "resume"
```

Affiche un tableau comparatif synthétique des différentes méthodes.

```python
MODE_AFFICHAGE = "detail"
```

Affiche les résultats détaillés des différentes configurations et les informations sur les tournées.

Pour enregistrer les graphiques sans ouvrir de fenêtre :

```python
AFFICHER_GRAPHIQUE = False
```

Les images sont enregistrées dans le dossier `resultats/`.

## 5. Format des instances

Les instances sont des fichiers texte dont les valeurs sont séparées par des points-virgules.

```text
n;<nombre de sommets, dépôts compris>
m;<nombre de véhicules>
tmax;<durée maximale par véhicule>
x;y;profit
x;y;profit
...
x;y;profit
```

La première ligne de coordonnées correspond au dépôt de départ, la dernière au dépôt d'arrivée et les lignes intermédiaires aux clients.

Les durées des trajets sont calculées à partir des distances euclidiennes entre les sommets.

## 6. Méthodes implémentées

### 6.1 Construction gloutonne

Deux méthodes sont proposées :

| Méthode | Principe |
|---|---|
| Séquentielle | Construit les tournées successivement, véhicule par véhicule. |
| Parallèle | Évalue les insertions possibles sur l'ensemble des véhicules à chaque itération. |

Chaque méthode est testée avec trois critères :

| Critère | Principe |
|---|---|
| `profit` | Privilégie les clients ayant le profit individuel le plus élevé. |
| `proche` | Privilégie les insertions ayant le plus faible surcoût de déplacement. |
| `ratio` | Privilégie le rapport entre le profit et le surcoût d'insertion. |

### 6.2 Amélioration des solutions

Les méthodes d'amélioration sont regroupées dans `optimisations.py`.

- **2-Opt :** modifie l'ordre des visites au sein d'une tournée afin de réduire sa durée.
- **Réinsertion :** tente d'ajouter des clients non visités lorsque les contraintes de durée le permettent.
- **Relocation :** déplace des clients entre les tournées pour améliorer leur organisation et libérer des marges de durée.
- **Boucle globale :** combine les opérateurs précédents de manière itérative afin de rechercher des solutions de meilleur profit.

Le programme compare les résultats après trois étapes : construction gloutonne, 2-Opt avec réinsertion, puis amélioration globale.

## 7. Résultats expérimentaux

Deux instances de référence ont été étudiées :

| Instance | Clients | Véhicules | Durée maximale | Meilleur profit connu |
|---|---:|---:|---:|---:|
| `p1.2.k` | 30 | 2 | 27,5 | 175 |
| `p7.4.q` | 100 | 4 | 85 | 909 |

Les meilleurs résultats obtenus sont :

| Instance | Méthode retenue | Profit obtenu | Clients visités | Écart au meilleur connu |
|---|---|---:|---:|---:|
| `p1.2.k` | Séquentielle — profit | 155 | 14 | 11,4 % |
| `p7.4.q` | Séquentielle — ratio + améliorations | 782 | 48 | 14,0 % |

Les résultats montrent notamment l'influence du critère de sélection sur les performances des constructions gloutonnes et l'intérêt des méthodes d'amélioration pour les instances plus grandes.

### Résultats affichés par le programme

Pour chaque configuration, le programme présente :

- Le profit et la durée après la construction gloutonne.
- Le profit et la durée après 2-Opt avec réinsertion.
- Le profit et la durée après amélioration globale.
- Le nombre de clients servis et les temps d'exécution.

Il affiche également les informations relatives à la meilleure solution : tournées des véhicules, profits individuels, durées et clients non visités.

Les tournées sont représentées graphiquement à l'aide de Matplotlib.

## 8. Vérification des contraintes

Les solutions sont construites de manière à respecter les principales contraintes du modèle mathématique :

- Chaque véhicule part du dépôt de départ et rejoint le dépôt d'arrivée.
- Chaque client est visité au plus une fois.
- Chaque tournée respecte la durée maximale autorisée.
- Les parcours sont continus et ne comportent pas de sous-tournées indépendantes des dépôts.

La fonction `solution_valide` permet notamment de contrôler le nombre de tournées, l'unicité des clients visités et le respect des durées maximales.

Une perspective d'amélioration consiste à développer une validation automatique exhaustive, couvrant explicitement toutes les contraintes de la formulation mathématique, notamment la conservation du flot et les liens entre variables de visite et de parcours.

## 9. Équipe

**Étudiants :**
- HOUNKPONOU Maxime — GitHub : `MaxAllegri`
- FAYE Ndeye Aminata Aida — GitHub : `NdeyeAminataAida`

**Enseignant :** Aziz Moukrim

**Université :** Université de Technologie de Compiègne (UTC)

**UV :** AI09 — Simulation et techniques d'optimisation