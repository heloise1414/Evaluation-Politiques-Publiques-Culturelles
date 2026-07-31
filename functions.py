# Fonction qui permet d'avoir les infos sur la base de données

import pandas as pd


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
    df[code_commune] = df[code_commune].astype(str).str.zfill(5)  #on met en forme le code commune
    a = len(df.index) - len(df[code_commune].unique())
    if a == 0:
        print("Une seule ligne par commune : jointure possible")
        return (True)
    else:
        print(str(a) + " communes sont présentent deux fois dans la base : jointure impossible")
        return (False)
