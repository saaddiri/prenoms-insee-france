import pandas as pd

LIBELLES_SEXE = {1: "Masculin", 2: "Féminin"}
ANNEE_EXHAUSTIVITE = 1946

def nettoyer_prenoms(df: pd.DataFrame) -> pd.DataFrame:
    propre = df.rename(columns={"periode": "annee" , "valeur": "naissances"})

    #R4
    propre["sexe_libelle"] = propre["sexe"].map(LIBELLES_SEXE)
    #R5
    propre["decennie"] = propre["annee"] // 10 * 10
    #R6
    propre["avant_1946"] = propre["annee"] < ANNEE_EXHAUSTIVITE

    #R7
    #total_diffuse contient le total de tous les bébés du même sexe et de la même année.
    total_diffuse = propre.groupby(["annee", "sexe"])["naissances"].transform("sum")
    propre["part_pour_10000"] = propre["naissances"] / total_diffuse * 10000
    return propre

if __name__ == "__main__" :
    from src.charger import charger_prenoms

    resultat = nettoyer_prenoms(charger_prenoms())
    print(resultat.shape)
    print(resultat.head(3).to_string())