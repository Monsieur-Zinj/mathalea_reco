"""
Exercise Manager Module

This module provides functionality to manage, update, and process exercise data
for an educational platform. It includes methods to fetch the latest exercises
from a remote source, process the data, and create both JSON and CSV outputs.

Classes:
    ExerciseManager: Manages all operations related to exercises.

Functions:
    main: Entry point of the script.
"""

import os
import json
import csv
import logging
from typing import Dict, Any
import requests
from src.config import Config

logger = logging.getLogger(__name__)

class ExerciseManager:
    """
    A class to manage exercise data operations.

    This class provides methods to fetch, process, update, and export exercise data.
    It interacts with both JSON and CSV file formats.

    Attributes:
        config (Config): Configuration object containing necessary settings.
        exercices_json_path (str): Path to the JSON file storing exercise data.
        exercices_csv_path (str): Path to the CSV file for storing interactive exercises.
        themes_json_path (str): Path to the JSON file storing themes data.
    """

    def __init__(self, config: Config):
        """
        Initialize the ExerciseManager with configuration settings.

        Args:
            config (Config): Configuration object containing necessary settings.
        """
        self.config = config
        self.exercices_json_path = os.path.join(config.data_dir, config.exercices_dir, config.exercices_json_filename)
        self.exercices_csv_path = os.path.join(config.data_dir, config.exercices_dir, 'exercices.csv')
        self.themes_json_path = os.path.join(config.data_dir, config.exercices_dir, 'themes.json')

    def process_exercices_all_json(self, exercices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the raw JSON data of exercises into a simplified dictionary format.

        This method recursively searches through the input dictionary to find
        exercise entries and restructures them into a flat dictionary with
        exercise references as keys.

        Args:
            exercices (Dict[str, Any]): Raw exercise data in nested dictionary format.

        Returns:
            Dict[str, Any]: Processed dictionary with exercise references as keys.
        """
        result = {}

        def process_item(item: Any):
            """
            Recursively process items in the exercise dictionary.

            Args:
                item (Any): The current item being processed.
            """
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, dict) and "ref" in value:
                        result[value["ref"]] = value
                    else:
                        process_item(value)
            elif isinstance(item, list):
                for element in item:
                    process_item(element)

        process_item(exercices)
        return result

    def fetch_latest_exercices(self) -> Dict[str, Any]:
        """
        Fetch the latest exercises from the remote source.

        This method sends a GET request to the specified URL and processes
        the returned JSON data.

        Returns:
            Dict[str, Any]: Processed dictionary of latest exercises, or an empty dict if an error occurs.
        """
        url = "https://forge.apps.education.fr/coopmaths/mathalea/-/raw/main/src/json/allExercice.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.process_exercices_all_json(response.json())
        except requests.RequestException as e:
            logger.error(f"Error fetching exercises: {e}")
            return {}
        except json.JSONDecodeError:
            logger.error("Error decoding JSON response")
            return {}

    def update_exercices(self):
        """
        Update the local JSON file with the latest exercises.

        This method fetches the latest exercises and writes them to the local JSON file.
        If the fetch operation fails, no update is performed.
        """
        logger.info(f"Updating exercises from {self.exercices_json_path}")
        
        latest_exercices = self.fetch_latest_exercices()
        if not latest_exercices:
            return

        with open(self.exercices_json_path, 'w') as f:
            json.dump(latest_exercices, f, indent=4)

        logger.info(f"Exercises updated successfully to {self.exercices_json_path}")

    def create_themes_json(self):
        """
        Create a themes.json file based on the levelsThemesList.json from the remote source.

        This method fetches the JSON data from the specified URL, processes it to extract
        themes and sub-themes, and writes the result to a themes.json file.
        """
        url = "https://forge.apps.education.fr/coopmaths/mathalea/-/raw/main/src/json/levelsThemesList.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            themes = {}
            for key, value in data.items():
                if isinstance(value, dict) and "titre" in value and "sousThemes" in value:
                    themes[key] = {
                        "titre": value["titre"],
                        "sousThemes": value["sousThemes"]
                    }

            with open(self.themes_json_path, 'w', encoding='utf-8') as f:
                json.dump(themes, f, ensure_ascii=False, indent=2)

            logger.info(f"Themes JSON file created successfully: {self.themes_json_path}")
        except requests.RequestException as e:
            logger.error(f"Error fetching themes data: {e}")
        except json.JSONDecodeError:
            logger.error("Error decoding JSON response for themes")
        except IOError as e:
            logger.error(f"Error writing themes JSON file: {e}")


    def process_exercise_reference(self, ref):
        # Charge les données de thèmes
        with open(self.themes_json_path, 'r', encoding='utf-8') as f:
            themes_data = json.load(f)

        theme = "Unknown"
        sub_theme = "Unknown"

        # Extrait le niveau et la clé de thème
        level = ref[0]
        theme_key = ref[:3]

        # Cherche le thème correspondant pour le niveau
        for key, value in themes_data.items():
            if key.startswith(level) and theme_key.startswith(key):
                theme = value['titre']
                # Cherche le sous-thème correspondant
                for sub_key, sub_value in value['sousThemes'].items():
                    if ref.startswith(sub_key):
                        sub_theme = sub_value
                        break
                break

        return {
            'theme': theme,
            'sub_theme': sub_theme
        }

    def create_exercices_csv(self):
        """
        Create a CSV file containing only interactive exercises with theme information.

        This method reads the JSON file of all exercises, filters for interactive ones,
        and writes them to a CSV file. The CSV includes the reference, title, UUID,
        theme, and sub-theme of each exercise.
        """
        try:
            with open(self.exercices_json_path, 'r', encoding='utf-8') as json_file:
                exercices = json.load(json_file)
        except FileNotFoundError:
            logger.error(f"JSON file not found: {self.exercices_json_path}")
            return

        csv_data = [['refs', 'titre', 'uuid', 'theme', 'sub_theme']]
        for ref, data in exercices.items():
            if data.get('tags', {}).get('interactif') == True:
                theme_info = self.process_exercise_reference(ref)
                csv_data.append([ref, data['titre'], data['uuid'], theme_info['theme'], theme_info['sub_theme']])

        try:
            with open(self.exercices_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows(csv_data)
            logger.info(f"CSV file with interactive exercises created successfully: {self.exercices_csv_path}")
        except IOError as e:
            logger.error(f"Error writing CSV file: {e}")

def main():
    """
    Main function to run the exercise update and file creation processes.

    This function initializes logging, creates an ExerciseManager instance,
    and calls the methods to update exercises, create the themes JSON file, and create the CSV file.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = Config()
    manager = ExerciseManager(config)
    manager.update_exercices()
    manager.create_themes_json()
    manager.create_exercices_csv()

if __name__ == "__main__":
    main()
