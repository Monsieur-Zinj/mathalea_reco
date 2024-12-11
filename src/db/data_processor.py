from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import urllib.parse
import re
from pathlib import Path
import os


class DataProcessor:
    def __init__(self, folder: str, config):
        self.folder = folder
        self.config = config
        print(f"Initializing DataProcessor with folder: {self.folder}")
        print(f"Config: {self.config.__dict__}")
        # self.ensure_output_directory()

    def ensure_output_directory(self) -> None:
        """Ensure the output directory exists"""
        output_dir = Path(self.config.final_data_dir)
        print(f"Ensuring output directory exists: {output_dir}")
        output_dir.mkdir(exist_ok=True)
        print(
            f"Output directory status: {'exists' if output_dir.exists() else 'creation failed'}"
        )

    def process_res(self) -> pd.DataFrame:
        """Process the results file"""
        print(f"Processing results file: {self.config.res_filename}")
        df = pd.read_csv(self._get_path(self.config.res_filename))

        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                pass  # Keep as is if conversion is not possible

        return df

    def process_eleve_groupe(self) -> pd.DataFrame:
        """Process the student group file"""
        file_path = os.path.join(
            self.config.data_dir, self.config.groupe_classe_filename
        )
        print(f"Processing student group file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        return pd.read_csv(file_path, usecols=["Élève", "Classe", "Groupe"])

    def process_meta(self) -> pd.DataFrame:
        """Process the metadata file"""
        print(f"Processing metadata file: {self.config.meta_filename}")
        df = pd.read_csv(self._get_path(self.config.meta_filename))

    def _get_path(self, filename: str) -> str:
        """Get the full path for a file"""
        full_path = os.path.join(self.folder, filename)
        print(f"Full path for {filename}: {full_path}")
        print(f"File exists: {os.path.exists(full_path)}")
        return full_path


class URLProcessor:
    @staticmethod
    def extract_url_from_html(content: str) -> str:
        """Extract URL from HTML content"""
        try:
            return content.split("URL=")[1].split('"></head></html>')[0]
        except IndexError:
            raise ValueError("Invalid HTML format")

    @staticmethod
    def parse_url(url: str) -> List[Dict]:
        """Parse URL and extract exercise information"""
        parsed_url = urllib.parse.urlparse(url)
        pattern = re.compile(r"(\w+)=([^&]+)")
        matches = pattern.findall(parsed_url.query)

        result = []
        current_dict = {}

        for key, value in matches:
            if key == "uuid" and current_dict:
                result.append(current_dict)
                current_dict = {}
            current_dict[key] = value

        if current_dict:
            result.append(current_dict)

        if result and all(k not in result[0] for k in ["id", "alea"]):
            result.pop(0)

        return [URLProcessor.create_super_id(d) for d in result]

    @staticmethod
    def create_super_id(exercise_dict: Dict) -> Dict:
        """Create a super ID for an exercise"""
        components = [
            exercise_dict.get("id", ""),
            # exercise_dict.get("alea", ""),
            # exercise_dict.get("n", ""),
            exercise_dict.get("s", ""),
        ]
        components.extend(exercise_dict.get(f"s{i}", "NA") for i in range(2, 10))

        return {
            "super_id": "_".join(str(comp) for comp in components if comp),
            **exercise_dict,
        }


class DataAnalyzer:
    def __init__(
        self, df_res: pd.DataFrame, df_groupe: pd.DataFrame, url_dict: List[Dict]
    ):
        self.df_res = df_res
        self.df_groupe = df_groupe
        self.url_dict = url_dict

    def prepare_final_dataframe(self) -> pd.DataFrame:
        """Prepare the final dataframe with all necessary transformations"""
        df = self.df_res.join(self.df_groupe.set_index("Élève"), on="Élève")
        print("Columns before renaming:")
        print(df.columns)
        # get numeric columns : columns in which the name contains some numbers

        numeric_columns = [
            col
            for col in df.columns
            if any(char.isdigit() for char in col)
        ]
        print("Numeric columns:")
        print(numeric_columns)

        columns = ["Élève", "Classe", "Groupe"] + numeric_columns
        df = df[columns]
        print("Columns after joining:")
        print(df.columns)
        print(len(self.url_dict))

        # Rename columns and normalize scores

        column_mapping = {
            numeric_columns[i]: self.url_dict[i]["super_id"]
            for i in range(0, len(self.url_dict))
        }
        df = df.rename(columns=column_mapping)
        print("Columns after renaming:")
        print(df.columns)

        self._update_missing_n_values(df)
        self._normalize_scores(df)

        return df

    def _update_missing_n_values(self, df: pd.DataFrame) -> None:
        """Update missing 'n' values in url_dict"""
        for d in self.url_dict:
            if "n" not in d:
                d["n"] = str(int(df[d["super_id"]].max()))

    def _normalize_scores(self, df: pd.DataFrame) -> None:
        """Normalize scores by dividing by n"""
        for d in self.url_dict:
            print(d["super_id"])
            print("n")
            print(d["n"])
            print(df[d["super_id"]].max())
            df[d["super_id"]] = df[d["super_id"]] / int(d["n"])
            print(df[d["super_id"]].max())
        
