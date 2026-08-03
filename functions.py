# Fonction qui permet d'avoir les infos sur la base de données

import pandas as pd
from cartiflette import carti_download
import matplotlib.pyplot as plt

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


def verifcom(df, code_commune):
    """Indiquer le df et le nom de la variable Code insee de la commune
    La fonction retourne True si la jointure peut être faite (une seule ligne par commune)
    Elle retourne False sinon"""
    df[code_commune] = df[code_commune].astype(str).str.zfill(5)  # on met en forme le code commune
    a = len(df.index) - len(df[code_commune].unique())
    if a == 0:
        print("Une seule ligne par commune : jointure possible")
        return (True)
    else:
        print(str(a) + " communes sont présentent deux fois dans la base : jointure impossible")
        return (False)


# ======================================================================================
# STATS DESC ET VISUALISATION
# ======================================================================================

# Récupération des contours des communes de France
communes = carti_download(
    values=["France"],
    crs=4326,
    borders="COMMUNE",
    vectorfile_format="geojson",
    filter_by="FRANCE_ENTIERE",
    source="EXPRESS-COG-CARTO-TERRITOIRE",
    year=2022
    )


def carte_com(df, code_insee, variable, couleur, titre):
    """
    Affiche une carte choroplèthe des communes.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les données à cartographier.
    code_insee : str
        Nom de la colonne contenant le code INSEE de la commune.
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
    # S'assurer que les codes INSEE sont bien au même format (string)
    communes["INSEE_COM"] = communes["INSEE_COM"].astype(str)
    df = df.copy()
    df[code_insee] = df[code_insee].astype(str)

    # Jointure entre la géométrie et les données
    carte = communes.merge(df, left_on="INSEE_COM", right_on=code_insee, how="inner")

    # Vérification qu'il y a bien des données après la jointure
    if carte.empty:
        print("⚠️ Aucune correspondance trouvée entre les codes INSEE des deux bases.")
        return

    print(carte[variable].isna().sum(), "/", len(carte))
    print(carte[variable].describe())

    # Affichage de la carte
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))  # ratio plus adapté à la métropole
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


def carte_com_cat(df, code_insee, variable, couleur, titre):
    """
    Affiche une carte choroplèthe des communes.

    Paramètres
    ----------
    df : pd.DataFrame
        DataFrame contenant les données à cartographier.
    code_insee : str
        Nom de la colonne contenant le code INSEE de la commune.
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
    # S'assurer que les codes INSEE sont bien au même format (string)
    communes["INSEE_COM"] = communes["INSEE_COM"].astype(str)
    df = df.copy()
    df[code_insee] = df[code_insee].astype(str)

    # Jointure entre la géométrie et les données
    carte = communes.merge(df, left_on="INSEE_COM", right_on=code_insee, how="inner")

    # Vérification qu'il y a bien des données après la jointure
    if carte.empty:
        print("⚠️ Aucune correspondance trouvée entre les codes INSEE des deux bases.")
        return

    print(carte[variable].isna().sum(), "/", len(carte))
    print(carte[variable].describe())

    # Affichage de la carte
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))  # ratio plus adapté à la métropole
    ax.set_aspect("equal")
    carte.plot(
        column=variable,
        cmap=couleur,
        scheme="quantiles",
        k=10,                  # nombre de classes
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
