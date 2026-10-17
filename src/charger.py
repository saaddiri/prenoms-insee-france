import pandas as pd
from src.config import COLONNES_ATTENDUES, FICHIER_NATIONAL

def charger_prenoms(chemin=FICHIER_NATIONAL) -> pd.DataFrame:
    df = pd.read_csv(chemin, sep=";", encoding="UTF-8", keep_default_na=False)
    if list(df.columns) != COLONNES_ATTENDUES :
        raise ValueError(
            f"Colonnes attendues : {list(df.columns)}"
            f"(attendu : {COLONNES_ATTENDUES})"
        )
    return df

if __name__ == "__main__" :
    donnees = charger_prenoms()
    print(donnees.shape)
    print(donnees.head(3))