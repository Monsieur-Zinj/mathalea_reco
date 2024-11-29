import json
from datetime import datetime
import pandas as pd
import os

def generate_json_data(df, tags, url_infos):
    current_time = datetime.now().isoformat()
    data = {
        "metadata": {
            "created_at": current_time,
            "updated_at": current_time
        },
        "tags": tags,
        "exercises": {},
        "students": {}
    }
    
    # Extract exercise information
    for i,col in enumerate(df.columns[3:]):  # Assuming first 3 columns are Élève, Classe, Groupe
        data["exercises"][col] = {
            "average_score": df[col].mean(),
            "max_score": df[col].max(),
            "min_score": df[col].min()
        }
        ## add url info
        data["exercises"][col].update(url_infos[i])


    
    # Extract student information
    for _, row in df.iterrows():
        student_name = row["Élève"]
        data["students"][student_name] = {
            "class": row["Classe"],
            "group": row["Groupe"],
            "scores": {col: row[col] for col in df.columns[3:] if pd.notna(row[col])}
        }
    
    return data

def update_or_create_json(json_path, new_data):
    current_time = datetime.now().isoformat()
    
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "metadata" not in data:
            data["metadata"] = {"created_at": current_time, "updated_at": current_time}
        else:
            if "created_at" not in data["metadata"]:
                data["metadata"]["created_at"] = current_time
            data["metadata"]["updated_at"] = current_time
        
        # Update other fields from new_data
        for key, value in new_data.items():
            if key != "metadata":
                data[key] = value
        
        print(f"Existing JSON file updated: {json_path}")
    else:
        data = new_data
        print(f"New JSON file created: {json_path}")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
