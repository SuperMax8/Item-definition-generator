#!/usr/bin/env python3
import os
import json

# Répertoires d'entrée et de sortie
models_dir = "assets/minecraft/models/klum/items"       # Dossier des modèles
items_dir = "assets/minecraft/items/klum/items"           # Dossier de sortie pour les items non boucliers
shield_item_file = "assets/minecraft/items/shield.json"   # Fichier de sortie unique pour les boucliers

# On s'assure que les dossiers de sortie existent
os.makedirs(items_dir, exist_ok=True)
os.makedirs(os.path.dirname(shield_item_file), exist_ok=True)

# Dictionnaire pour stocker les modèles de boucliers
# Clé : nom de base du bouclier (ex: "shield_leshield") -> {"normal": nom, "block": nom}
shield_models = {}
# Liste pour les autres modèles (non boucliers)
non_shield_files = []

# Parcours des fichiers de modèle
for filename in os.listdir(models_dir):
    if not filename.endswith(".json"):
        continue

    if filename.startswith("shield_"):
        # Variante block identifiée par "_block.json"
        if filename.endswith("_block.json"):
            base = filename[:-len("_block.json")]
            shield_models.setdefault(base, {})["block"] = filename[:-5]  # Retire l'extension .json
        # Variante normale identifiée par "_normal.json"
        elif filename.endswith("_normal.json"):
            base = filename[:-len("_normal.json")]
            shield_models.setdefault(base, {})["normal"] = base  # On enlève le suffixe _normal
        else:
            # Sinon, c'est un bouclier normal sans suffixe
            base = filename[:-5]
            shield_models.setdefault(base, {})["normal"] = base
    else:
        non_shield_files.append(filename)

# Génération des fichiers d'items pour les items non boucliers
for filename in non_shield_files:
    model_name = filename[:-5]  # retire ".json" pour obtenir le nom du modèle
    # Création du JSON d'item respectant le format demandé
    item_content = {
        "model": {
            "model": "minecraft:klum/items/" + model_name,
            "tints": [
                {
                    "index": 0,
                    "default": 16777215,
                    "type": "minecraft:custom_model_data"
                }
            ],
            "type": "minecraft:model"
        }
    }
    output_path = os.path.join(items_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(item_content, f, indent=4)
    print(f"Fichier d'item généré pour '{model_name}' : {output_path}")

# Génération du fichier shield.json pour les boucliers
if shield_models:
    cases = []
    # Pour chaque bouclier, on vérifie que les deux variantes existent
    for shield, variants in sorted(shield_models.items()):
        if "normal" in variants and "block" in variants:
            case_entry = {
                "when": shield,  # ex: "shield_leshield"
                "model": {
                    "type": "minecraft:condition",
                    "property": "minecraft:using_item",
                    "on_false": {
                        "type": "model",
                        "model": "minecraft:klum/items/" + variants["normal"]
                    },
                    "on_true": {
                        "type": "model",
                        "model": "minecraft:klum/items/" + variants["block"]
                    }
                }
            }
            cases.append(case_entry)
        else:
            print(f"Avertissement : Le bouclier '{shield}' n'a pas les deux variantes (normal et _block). Il est ignoré.")

    if cases:
        # Pour le fallback, on prend par exemple la version normale du premier bouclier par ordre alphabétique
        first_shield = sorted(shield_models.keys())[0]
        fallback_model = "minecraft:klum/items/" + shield_models[first_shield]["normal"]

        shield_item = {
            "model": {
                "type": "select",
                "property": "custom_model_data",
                "index": 0,
                "fallback": {
                    "type": "model",
                    "model": fallback_model
                },
                "cases": cases
            }
        }
        with open(shield_item_file, "w", encoding="utf-8") as f:
            json.dump(shield_item, f, indent=4)
        print(f"Fichier d'item pour boucliers généré : {shield_item_file}")
    else:
        print("Aucun bouclier complet (avec variantes normale et _block) n'a été trouvé.")
