# Fonction qui permet d'avoir les infos sur la base de données

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
