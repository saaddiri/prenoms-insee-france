import pandas as pd
from src.nettoyer import LIBELLES_SEXE

def serie_prenom(df: pd.DataFrame, prenom: str, sexe: int) -> pd.DataFrame :
    selection = df[(df["prenom"] == prenom.upper()) & (df["sexe"] == sexe)]
    if selection.empty:
        raise ValueError(f"Prénom introuvable : {prenom} (sexe {sexe})")

    toutes_les_annees = range(int(df["annee"].min()), int(df["annee"].max()) + 1)
    serie = (
        selection.set_index("annee")[["naissances", "part_pour_10000"]]
        .reindex(toutes_les_annees)
    )
    serie.index.name = "annee"
    return serie

def pic_et_minimum(serie: pd.DataFrame, colonne: str = "naissances") -> dict:
    valeurs = serie[colonne].dropna()
    return {
        "annee_pic": int(valeurs.idxmax()),
        "valeur_pic": float(valeurs.max()),
        "annee_min": int(valeurs.idxmin()),
        "valeur_min": float(valeurs.min()),
        "annees_diffusees": int(valeurs.size),
        "annees_absentes": int(serie[colonne].isna().sum()),
    }

def comparer_prenoms(df, choix, colonne="part_pour_10000", debut=None, fin=None):
    colonnes = {}
    for prenom, sexe in choix:
        nom = f"{prenom.upper()} ({LIBELLES_SEXE[sexe]})"
        colonnes[nom] = serie_prenom(df, prenom, sexe)[colonne]
    return pd.DataFrame(colonnes).loc[debut:fin]

def top_par_decennie(df: pd.DataFrame, sexe: int, n: int = 10) -> pd.DataFrame:
    """Les n prénoms les plus donnés dans chaque décennie, pour un sexe."""
    totaux = (
        df[df["sexe"] == sexe]
        .groupby(["decennie", "prenom"], as_index=False)["naissances"]
        .sum()
        .sort_values(["decennie", "naissances", "prenom"], ascending=[True, False, True])
    )
    totaux["rang_decennie"] = totaux.groupby("decennie").cumcount() + 1

    annees_par_decennie = df.groupby("decennie")["annee"].nunique()
    totaux["nb_annees"] = totaux["decennie"].map(annees_par_decennie)

    return totaux[totaux["rang_decennie"] <= n].reset_index(drop=True)

def resume_periode(df: pd.DataFrame, debut: int, fin: int) -> pd.DataFrame:
    """Résume chaque prénom sur la période debut-fin (bornes incluses)."""
    sous_tableau = df[(df["annee"] >= debut) & (df["annee"] <= fin)]
    return (
        sous_tableau.groupby(["sexe", "prenom"])
        .agg(
            part_moyenne=("part_pour_10000", "mean"),
            naissances=("naissances", "sum"),
            annees_diffusees=("annee", "nunique"),
        )
    )

def tendances(df: pd.DataFrame, duree: int = 25) -> pd.DataFrame:
    """Compare chaque prénom entre la période récente et la période précédente."""
    derniere = int(df["annee"].max())
    recente = resume_periode(df, derniere - duree + 1, derniere)
    precedente = resume_periode(df, derniere - 2 * duree + 1, derniere - duree)

    tableau = recente.join(
        precedente, lsuffix="_recente", rsuffix="_precedente", how="inner"
    )
    tableau["variation_part"] = (
        tableau["part_moyenne_recente"] - tableau["part_moyenne_precedente"]
    )
    return tableau

def hausses_et_baisses(tableau: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Les n plus fortes hausses et les n plus fortes baisses (en points)."""
    hausses = tableau.nlargest(n, "variation_part").assign(tendance="Hausse")
    baisses = tableau.nsmallest(n, "variation_part").assign(tendance="Baisse")
    return pd.concat([hausses, baisses]).reset_index()

