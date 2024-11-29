from src.config import Config
import requests
import json
import os

# @dataclass
# class Config:
#     """Configuration for file paths and constants"""
#     res_filename: str = "res.csv"
#     url_filename: str = "mathAlea.html"
#     meta_filename: str = "meta.csv"
#     groupe_classe_filename: str = "eleve_groupe.csv"
#     final_data_dir: str = "final_data"
#     activity_dir: str = os.path.join("data", "Activités")
#     source_data_dir: str = "source_data"
#     data_dir: str = "data"  # Added data_dir attribute
#     resultat_csv_filename: str = "resultat.csv"
#     resultat_json_filename: str = "resultat.json"
#     synthesis_data_dir: str = "synthesis_data"
#     synthesis_csv_filename: str = "synthesis.csv"
#     synthesis_json_filename: str = "synthesis.json"

#     exercices_dir: str = "exercices"
#     exercices_json_filename: str = "exercices.json"
    
#     # Updated activity name to match the folder structure
#     activity: str = os.getenv('MATHALEA_ACTIVITY', '1-Calcul_littéral')

#     def __post_init__(self):
#         # Ensure the activity is set correctly
#         if not self.activity:
#             self.activity = '1-Calcul_littéral'

# https://forge.apps.education.fr/coopmaths/mathalea/-/blob/main/src/json/allExercice.json



    # exercices.json
# {
#     "5e": {
#         "5A1": {
#             "5A10": {
#                 "ref": "5A10",
#                 "uuid": "4828d",
#                 "url": "5e/5A10.js",
#                 "titre": "\u00c9crire la liste de tous les diviseurs d'un entier",
#                 "dateDeModifImportante": "28/10/2021",
#                 "tags": {
#                     "interactif": true,
#                     "interactifType": "mathLive"
#                 }
#             },
# chercher récursivement la "ref" pour chaque exercice
# le transformer en dict avec la ref comme clé et le reste comme valeur
def process_exercices_all_json(exercices):
    result = {}

    def process_item(item):
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, dict) and "ref" in value:
                    # Found an exercise, add it to the result
                    result[value["ref"]] = value
                else:
                    # Recurse into nested dictionaries
                    process_item(value)
        elif isinstance(item, list):
            # Recurse into lists
            for element in item:
                process_item(element)

    process_item(exercices)
    print(json.dumps(result, indent=4))
    return result

def update_exercice():
    config = Config()
    exercices_json_path = os.path.join(config.data_dir, config.exercices_dir, config.exercices_json_filename)
    print(f"Updating exercices from {exercices_json_path}")
    # Get the JSON data if it exists
    try:
        with open(exercices_json_path, 'r') as f:
            exercices = json.load(f)
    except FileNotFoundError:
        exercices = {}

    # Get the latest exercices from the API
    url = "https://forge.apps.education.fr/coopmaths/mathalea/-/raw/main/src/json/allExercice.json"
    response = requests.get(url)
    response.raise_for_status()
    try:
        latest_exercices = process_exercices_all_json(response.json())
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response")
        return

    # Update the exercices
    

    # Save the updated exercices or create, erase and save
    with open(exercices_json_path, 'w') as f:
        json.dump(latest_exercices, f, indent=4)

    print(f"Exercices updated successfully to {exercices_json_path}")


if __name__ == "__main__":
    update_exercice()
