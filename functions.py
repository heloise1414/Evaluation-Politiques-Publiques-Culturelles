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
