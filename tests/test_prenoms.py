import pandas as pd
import pytest

from src.charger import charger_prenoms
from src.indicateurs import pic_et_minimum, serie_prenom, tendances, top_par_decennie
from src.nettoyer import nettoyer_prenoms


def petit_tableau() -> pd.DataFrame:
    """Mini-jeu de données inventé, dont on connaît les résultats à la main."""
    brut = pd.DataFrame(
        {
            "sexe": [1, 1, 1, 1, 1],
            "prenom": ["ALEX", "ALEX", "BRUNO", "BRUNO", "BRUNO"],
            "periode": [2000, 2002, 2000, 2001, 2002],
            "valeur": [10, 30, 90, 70, 70],
            "rang": [2, 2, 1, 1, 1],
        }
    )
    return nettoyer_prenoms(brut)


# ---------- Tests unitaires (petites données) ----------

def test_part_somme_10000_par_annee_et_sexe():
    petit = petit_tableau()
    sommes = petit.groupby(["annee", "sexe"])["part_pour_10000"].sum()
    assert sommes.tolist() == pytest.approx([10000, 10000, 10000])


def test_annee_absente_reste_nan_et_pas_zero():
    serie = serie_prenom(petit_tableau(), "alex", 1)
    assert list(serie.index) == [2000, 2001, 2002]
    assert serie.loc[2000, "naissances"] == 10
    assert pd.isna(serie.loc[2001, "naissances"])


def test_prenom_inconnu_leve_une_erreur():
    with pytest.raises(ValueError):
        serie_prenom(petit_tableau(), "ZZZ", 1)


def test_pic_et_minimum():
    serie = serie_prenom(petit_tableau(), "ALEX", 1)
    resultat = pic_et_minimum(serie)
    assert resultat["annee_pic"] == 2002
    assert resultat["valeur_pic"] == 30
    assert resultat["annee_min"] == 2000
    assert resultat["annees_diffusees"] == 2
    assert resultat["annees_absentes"] == 1


def test_top_par_decennie_classe_le_plus_donne_en_premier():
    top = top_par_decennie(petit_tableau(), sexe=1, n=1)
    assert top.loc[0, "prenom"] == "BRUNO"
    assert top.loc[0, "naissances"] == 230
    assert top.loc[0, "rang_decennie"] == 1
    assert top.loc[0, "nb_annees"] == 3


# ---------- Tests sur les vraies données INSEE ----------

@pytest.fixture(scope="module")
def brut():
    return charger_prenoms()


@pytest.fixture(scope="module")
def prenoms(brut):
    return nettoyer_prenoms(brut)


def test_aucune_ligne_perdue(brut, prenoms):
    assert len(prenoms) == len(brut)


def test_pas_de_doublon_sur_la_cle(prenoms):
    assert not prenoms.duplicated(["sexe", "prenom", "annee"]).any()


def test_tous_les_sexes_ont_un_libelle(prenoms):
    assert prenoms["sexe_libelle"].notna().all()


def test_parts_somment_a_10000_sur_les_vraies_donnees(prenoms):
    sommes = prenoms.groupby(["annee", "sexe"])["part_pour_10000"].sum()
    assert (sommes - 10000).abs().max() < 1e-6


def test_decennie_2020_est_signalee_incomplete(prenoms):
    top = top_par_decennie(prenoms, sexe=2, n=1)
    assert top.loc[top["decennie"] == 2020, "nb_annees"].iloc[0] == 6


def test_tendances_sans_valeur_manquante(prenoms):
    assert tendances(prenoms).isna().sum().sum() == 0