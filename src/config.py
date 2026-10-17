from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_BRUT = RACINE / "data" / "raw"
DOSSIER_TRAITE = RACINE / "data" / "processed"
FICHIER_NATIONAL = DOSSIER_BRUT / "prenoms-2025-nat.csv"

# Colonnes que le fichier INSEE doit contenir, dans cet ordre.
# Les noms changent d'une édition à l'autre (ex. PREUSUEL -> PRENOM),
# donc on les note ici pour détecter tout changement.
# Une seule liste à modifier si l'INSEE change son format.
COLONNES_ATTENDUES = ["sexe", "prenom", "periode", "valeur", "rang"]