import pandas as pd

from src.charger import charger_prenoms
from src.config import DOSSIER_TRAITE
from src.indicateurs import hausses_et_baisses, tendances, top_par_decennie
from src.nettoyer import LIBELLES_SEXE, nettoyer_prenoms


def executer() -> None:
    """Lit le fichier INSEE, calcule les tables et les écrit dans data/processed."""
    DOSSIER_TRAITE.mkdir(parents=True, exist_ok=True)

    prenoms = nettoyer_prenoms(charger_prenoms())

    faits = prenoms[["sexe", "prenom", "annee", "naissances", "rang", "part_pour_10000"]]
    dim_annee = (
        prenoms[["annee", "decennie", "avant_1946"]]
        .drop_duplicates()
        .sort_values("annee")
    )
    dim_sexe = pd.DataFrame(
        list(LIBELLES_SEXE.items()), columns=["sexe", "sexe_libelle"]
    )

    tops = []
    for sexe in LIBELLES_SEXE:
        tops.append(top_par_decennie(prenoms, sexe=sexe).assign(sexe=sexe))
    top_decennies = pd.concat(tops, ignore_index=True)

    evolutions = hausses_et_baisses(tendances(prenoms), n=10)

    sorties = {
        "faits_prenoms.csv": faits,
        "dim_annee.csv": dim_annee,
        "dim_sexe.csv": dim_sexe,
        "top_par_decennie.csv": top_decennies,
        "hausses_baisses.csv": evolutions,
    }
    for nom_fichier, tableau in sorties.items():
        tableau.to_csv(DOSSIER_TRAITE / nom_fichier, index=False, encoding="utf-8-sig")
        print(f"{nom_fichier} : {len(tableau)} lignes")


if __name__ == "__main__":
    executer()