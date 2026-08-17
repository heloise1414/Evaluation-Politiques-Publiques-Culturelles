# Fonction qui permet d'avoir les infos sur la base de données

import pandas as pd
from cartiflette import carti_download
import matplotlib.pyplot as plt
import numpy as np

# ======================================================================================
# PREPARATION DES DONNEES
# ======================================================================================


def importdata(path, separateur_csv):
    """import base de données CSV, chemin et séparateur du csv"""
    return (pd.read_csv(path, sep=separateur_csv, encoding="utf-8"))


def infosbase(df):
    print("=" * 60)
    print("DIMENSIONS DU JEU DE DONNÉES")
    print("=" * 60)
    print(f"Nombre de lignes    : {df.shape[0]}")
    print(f"Nombre de colonnes  : {df.shape[1]}")
    print("\n" + "=" * 60)
    print("NOMS DES COLONNES ET TYPES")
    print("=" * 60)
    print(df.dtypes)


def verifdep(df, code_insee):
    """Indiquer le df et le nom de la variable Code insee du departement
    La fonction retourne True si la jointure peut être faite (une seule ligne par commune)
    Elle retourne False sinon"""
    df[code_insee] = df[code_insee].astype(str).str.zfill(2)  # on met en forme le code commune
    a = len(df.index) - len(df[code_insee].unique())
    if a == 0:
        print("Une seule ligne par département : jointure possible")
        return (True)
    else:
        print(str(a) + " départements sont présents deux fois dans la base : jointure impossible")
        return (False)


# ======================================================================================
# STATS DESC ET VISUALISATION
# ======================================================================================

# Récupération des contours des départements de France

departements = carti_download(
    values=["France"],
    crs=4326,
    borders="DEPARTEMENT",
    vectorfile_format="geojson",
    filter_by="FRANCE_ENTIERE",
    source="EXPRESS-COG-CARTO-TERRITOIRE",
    year=2022
    )


def carte_dep(df, code_insee, variable, couleur, titre):
    """
    Affiche une carte choroplèthe des départements.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les données à cartographier.
    code_insee : str
        Nom de la colonne contenant le code INSEE (commune ou département).
        Si code commune, les 2 premiers caractères seront utilisés comme code département.
    variable : str
        Nom de la colonne contenant la variable à représenter.
    couleur : str
        Colormap matplotlib à utiliser (ex: 'viridis', 'OrRd', 'Blues').
    titre : str
        Titre de la carte.

    Retour
    ------
    None (affiche la carte)
    """
    departements["INSEE_DEP"] = departements["INSEE_DEP"].astype(str)
    df = df.copy()
    df[code_insee] = df[code_insee].astype(str)

    # Jointure entre la géométrie et les données
    carte = departements.merge(df, left_on="INSEE_DEP", right_on="code_insee", how="inner")

    if carte.empty:
        print("⚠️ Aucune correspondance trouvée entre les codes INSEE des deux bases.")
        return

    print(carte[variable].isna().sum(), "/", len(carte))
    print(carte[variable].describe())

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_aspect("equal")
    carte.plot(
        column=variable,
        cmap=couleur,
        linewidth=0.3,
        edgecolor="grey",
        legend=True,
        ax=ax,
        missing_kwds={"color": "green", "label": "Non disponible"}
    )

    ax.set_title(titre, fontsize=16)
    ax.set_xlim(-5, 10)
    ax.set_ylim(41, 51.5)
    ax.axis("off")
    plt.tight_layout()
    plt.show()


# ======================================================================================
# SIMULATION DES DONNEES
# ======================================================================================

def ipf(table_init, marges, col_valeur="effectif", max_iter=1000, tol=1e-6):
    """
    Ajustement proportionnel itératif (Iterative Proportional Fitting / raking).

    Permet de caler une table de contingence multi-dimensionnelle (loi jointe
    approchée, par exemple obtenue sous hypothèse d'indépendance) sur des
    marges connues (lois marginales observées dans le rapport).

    Paramètres
    ----------
    table_init : pd.DataFrame
        Table "longue" contenant une colonne par variable catégorielle
        (ex: "Age", "Statut") et une colonne de valeurs initiales
        (col_valeur), typiquement des effectifs ou probabilités de départ
        (souvent construite sous hypothèse d'indépendance : produit des
        marges normalisées).

    marges : dict[str, pd.Series]
        Dictionnaire {nom_de_variable: Series indexée par les modalités de
        la variable, contenant les totaux marginaux cibles (effectifs ou
        proportions x N)}. Une entrée par variable à caler.

    col_valeur : str
        Nom de la colonne contenant les valeurs à ajuster dans table_init.

    max_iter : int
        Nombre maximal d'itérations.

    tol : float
        Seuil de convergence : on arrête quand l'écart relatif maximal
        entre marges recalculées et marges cibles passe sous ce seuil.

    Retour
    ------
    pd.DataFrame
        Une copie de table_init dont la colonne col_valeur a été ajustée
        pour respecter (approximativement) toutes les marges fournies.

    Principe
    --------
    À chaque itération, pour chaque variable à caler, on recalcule la marge
    courante de la table (somme des valeurs par modalité), puis on
    multiplie chaque ligne par le ratio (marge cible / marge courante) de
    la modalité correspondante. On répète pour toutes les variables jusqu'à
    convergence. C'est l'algorithme classique de raking utilisé en
    post-stratification / calage sur marges.
    """
    table = table_init.copy()
    variables = list(marges.keys())

    for variable in variables:
        if variable not in table.columns:
            raise ValueError(f"La variable '{variable}' n'est pas une colonne de table_init.")

    for iteration in range(max_iter):
        ecart_max = 0.0

        for variable in variables:
            cible = marges[variable]

            # marge courante = somme des valeurs par modalité de la variable
            marge_courante = table.groupby(variable)[col_valeur].sum()

            # on s'assure d'avoir les mêmes modalités des deux côtés
            modalites = marge_courante.index.union(cible.index)
            marge_courante = marge_courante.reindex(modalites, fill_value=0.0)
            cible_alignee = cible.reindex(modalites, fill_value=0.0)

            # ratio de correction par modalité (on évite la division par 0)
            ratio = (cible_alignee / marge_courante.replace(0, np.nan)).fillna(0.0)

            ecart_max = max(ecart_max, np.abs(marge_courante - cible_alignee).max())

            # on applique le ratio à chaque ligne selon sa modalité
            table[col_valeur] = table[col_valeur] * table[variable].map(ratio).astype(float)

        if ecart_max < tol:
            break

    return table


def table_independance(marges, col_valeur="effectif"):
    """
    Construit une table jointe initiale sous hypothèse d'indépendance,
    à partir de plusieurs marges (produit cartésien des modalités,
    valeur = produit des proportions marginales).

    Paramètres
    ----------
    marges : dict[str, pd.Series]
        Comme pour ipf() : {nom_de_variable: Series des totaux marginaux}.

    Retour
    ------
    pd.DataFrame
        Table longue avec une colonne par variable + col_valeur, prête à
        être passée à ipf() comme table_init.
    """
    variables = list(marges.keys())

    # on normalise chaque marge pour obtenir des proportions
    proportions = {var: marges[var] / marges[var].sum() for var in variables}

    # produit cartésien des modalités de toutes les variables
    index_grids = pd.MultiIndex.from_product(
        [proportions[var].index for var in variables], names=variables
    )
    table = index_grids.to_frame(index=False)

    # valeur initiale = produit des proportions marginales (indépendance)
    table[col_valeur] = 1.0
    for var in variables:
        table[col_valeur] *= table[var].map(proportions[var])

    return table


def simuler_individus_depuis_table(table_calee, col_valeur="effectif", nb_indiv=10_000, rng=None):
    """
    Tire aléatoirement nb_indiv individus à partir d'une table jointe calée
    (résultat de ipf()), interprétée comme une distribution de probabilité
    multivariée.

    Paramètres
    ----------
    table_calee : pd.DataFrame
        Table longue avec les colonnes catégorielles + col_valeur (poids,
        non nécessairement normalisés).

    col_valeur : str
        Colonne contenant les poids / probabilités non normalisées.

    nb_indiv : int
        Taille de l'échantillon à simuler.

    rng : np.random.Generator, optionnel
        Générateur aléatoire (pour la reproductibilité). Si None, un
        générateur par défaut est créé.

    Retour
    ------
    pd.DataFrame
        Base de données simulée au niveau individuel, une ligne par
        individu, avec les variables catégorielles issues de table_calee.
    """
    if rng is None:
        rng = np.random.default_rng()

    poids = table_calee[col_valeur].to_numpy(dtype=float)
    proba = poids / poids.sum()

    variables = [c for c in table_calee.columns if c != col_valeur]

    tirages = rng.choice(len(table_calee), size=nb_indiv, p=proba)

    df_simule = table_calee.iloc[tirages][variables].reset_index(drop=True)
    return df_simule


def valider_simulation(df_simule, marges_cibles, normaliser=True):
    """
    Ré-agrège la base simulée au niveau individuel et compare les
    proportions/effectifs obtenus aux statistiques d'origine (marges
    cibles issues du rapport de la Cour des comptes).

    Paramètres
    ----------
    df_simule : pd.DataFrame
        Base individuelle simulée (sortie de simuler_individus_depuis_table
        ou de toute autre méthode de simulation).

    marges_cibles : dict[str, pd.Series]
        {nom_de_variable: Series des proportions ou effectifs cibles par
        modalité}, telles qu'extraites des tableaux de la Cour des comptes.

    normaliser : bool
        Si True, compare des proportions (entre 0 et 1) plutôt que des
        effectifs bruts.

    Retour
    ------
    dict[str, pd.DataFrame]
        Pour chaque variable, un DataFrame avec les colonnes
        ["simule", "cible", "ecart", "ecart_relatif"] indexé par modalité,
        permettant de vérifier visuellement la qualité du calage.
    """
    resultats = {}

    for variable, cible in marges_cibles.items():
        if variable not in df_simule.columns:
            raise ValueError(f"La variable '{variable}' n'est pas présente dans df_simule.")

        marge_simulee = df_simule[variable].value_counts()

        if normaliser:
            marge_simulee = marge_simulee / marge_simulee.sum()
            cible_comparee = cible / cible.sum()
        else:
            cible_comparee = cible

        modalites = marge_simulee.index.union(cible_comparee.index)
        marge_simulee = marge_simulee.reindex(modalites, fill_value=0.0)
        cible_comparee = cible_comparee.reindex(modalites, fill_value=0.0)

        comparaison = pd.DataFrame({
            "simule": marge_simulee,
            "cible": cible_comparee,
        })
        comparaison["ecart"] = comparaison["simule"] - comparaison["cible"]
        comparaison["ecart_relatif"] = (
            comparaison["ecart"] / comparaison["cible"].replace(0, np.nan)
        )

        resultats[variable] = comparaison.sort_index()

    return resultats
