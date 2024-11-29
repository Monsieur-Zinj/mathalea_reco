from dataclasses import dataclass
import os

@dataclass
class Config:
    """Configuration for file paths and constants"""
    res_filename: str = "res.csv"
    url_filename: str = "mathAlea.html"
    meta_filename: str = "meta.csv"
    groupe_classe_filename: str = "eleve_groupe.csv"
    final_data_dir: str = "final_data"
    activity_dir: str = os.path.join("data", "Activités")
    source_data_dir: str = "source_data"
    data_dir: str = "data"  # Added data_dir attribute
    resultat_csv_filename: str = "resultat.csv"
    resultat_json_filename: str = "resultat.json"
    synthesis_data_dir: str = "synthesis_data"
    synthesis_csv_filename: str = "synthesis.csv"
    synthesis_json_filename: str = "synthesis.json"

    exercices_dir: str = "exercices"
    exercices_json_filename: str = "exercices.json"
    
    # Updated activity name to match the folder structure
    activity: str = os.getenv('MATHALEA_ACTIVITY', '1-Calcul_littéral')

    def __post_init__(self):
        # Ensure the activity is set correctly
        if not self.activity:
            self.activity = '1-Calcul_littéral'
