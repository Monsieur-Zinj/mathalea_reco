import json
import sys
import os
import csv
from collections import defaultdict
from datetime import datetime
from src.config import Config


def update_synthesis_files(synthesis_csv, synthesis_json, new_json, activity_name):
    # Charger les données existantes
    try:
        with open(synthesis_json, 'r') as f:
            synthesis_data = json.load(f)
    except FileNotFoundError:
        synthesis_data = {
            "tags": {},
            "exercises": {},
            "students": {},
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "synthesized_activities": []
            }
        }

    # Charger les nouvelles données
    with open(new_json, 'r') as f:
        new_data = json.load(f)

    # Vérifier si l'activité a déjà été synthétisée
    # Si oui, demander à l'utilisateur s'il veut continuer
    if activity_name in synthesis_data['metadata']['synthesized_activities']:
        print(f"L'activité {activity_name} a déjà été synthétisée. Voulez-vous continuer ? (o-y/n")
        response = input()
        if response.lower() not in ['o', 'y']:
            return
        

    # Mettre à jour les exercices
    for exercise_id, exercise_info in new_data['exercises'].items():
        if False: # exercise_id not in synthesis_data['exercises']:
            synthesis_data['exercises'][exercise_id] = exercise_info
            synthesis_data['exercises'][exercise_id]['activities'] = [activity_name]
        else:
            synthesis_data['exercises'][exercise_id]['n'] += exercise_info['n']
            if activity_name not in synthesis_data['exercises'][exercise_id]['activities']:
                synthesis_data['exercises'][exercise_id]['activities'].append(activity_name)
            # Mise à jour de la moyenne glissante
            old_avg = synthesis_data['exercises'][exercise_id]['average_score']
            old_n = int(synthesis_data['exercises'][exercise_id]['n']) - int(exercise_info['n'])
            new_avg = exercise_info['average_score']
            updated_avg = (old_avg * old_n + new_avg * exercise_info['n']) / synthesis_data['exercises'][exercise_id]['n']
            synthesis_data['exercises'][exercise_id]['average_score'] = updated_avg

    # Mettre à jour les étudiants
    for student, student_info in new_data['students'].items():
        if student not in synthesis_data['students']:
            synthesis_data['students'][student] = student_info
            synthesis_data['students'][student]['activities'] = [activity_name]
        else:
            if activity_name not in synthesis_data['students'][student]['activities']:
                synthesis_data['students'][student]['activities'].append(activity_name)
            for exercise_id, score in student_info['scores'].items():
                if exercise_id not in synthesis_data['students'][student]['scores']:
                    synthesis_data['students'][student]['scores'][exercise_id] = score
                else:
                    # Mise à jour de la moyenne glissante pour le score de l'étudiant
                    old_score = synthesis_data['students'][student]['scores'][exercise_id]
                    n = synthesis_data['exercises'][exercise_id]['n']
                    updated_score = (old_score * (n-1) + score) / n
                    synthesis_data['students'][student]['scores'][exercise_id] = updated_score

    # Calculer la somme de tous les "n" des exercices
    total_n = sum(exercise['n'] for exercise in synthesis_data['exercises'].values())

    # Mettre à jour les métadonnées
    synthesis_data['metadata']['updated_at'] = datetime.now().isoformat()
    synthesis_data['metadata']['synthesized_activities'].append(activity_name)
    synthesis_data['metadata']['total_n'] = total_n

    # Calculer des statistiques globales
    total_exercises = len(synthesis_data['exercises'])
    total_students = len(synthesis_data['students'])
    average_score_all_exercises = sum(ex['average_score'] for ex in synthesis_data['exercises'].values()) / total_exercises

    synthesis_data['metadata']['statistics'] = {
        'total_exercises': total_exercises,
        'total_students': total_students,
        'average_score_all_exercises': average_score_all_exercises,
        'total_n': total_n
    }
    

    # Sauvegarder le JSON mis à jour
    with open(synthesis_json, 'w') as f:
        json.dump(synthesis_data, f, indent=2)

    # Mettre à jour le CSV
    headers = ['Élève', 'Classe', 'Groupe'] + list(synthesis_data['exercises'].keys())
    rows = []
    for student, student_info in synthesis_data['students'].items():
        row = [student, student_info['class'], student_info['group']]
        for exercise_id in synthesis_data['exercises'].keys():
            row.append(student_info['scores'].get(exercise_id, ''))
        rows.append(row)

    

    print(f"Synthèse mise à jour avec l'activité {activity_name}")

  

    with open(synthesis_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)



# @dataclass
# class Config:
#     """Configuration for file paths and constants"""
#     res_filename: str = "res.csv"
#     url_filename: str = "mathAlea.html"
#     meta_filename: str = "meta.csv"
#     groupe_classe_filename: str = "eleve_groupe.csv"
#     final_data_dir: str = "final_data"
#     source_data_dir: str = os.path.join("data", "Activités")
#     data_dir: str = "data"  # Added data_dir attribute
#     resultat_csv_filename: str = "resultat.csv"
#     resultat_json_filename: str = "resultat.json"
#     synthesis_data_dir: str = "synthesis_data"
#     synthesis_csv_filename: str = "synthesis.csv"
#     synthesis_json_filename: str = "synthesis.json"


def main():
    # récupérer l'argument : le nom de l'activité
    if len(sys.argv) > 1:
        activity = sys.argv[1]
    else:
        raise ValueError("Veuillez fournir le nom de l'activité en argument")
    
    # Charger la configuration
    config = Config()

    synthesis_data_dir = os.path.join(config.data_dir, config.synthesis_data_dir)
    synthesis_csv = os.path.join(synthesis_data_dir, config.synthesis_csv_filename)
    synthesis_json = os.path.join(synthesis_data_dir, config.synthesis_json_filename)

    activity_dir = os.path.join(config.activity_dir, activity)
    source_data_activity_dir = os.path.join(activity_dir, config.source_data_dir)
    activity_json = os.path.join(activity_dir, config.final_data_dir, config.resultat_json_filename)
    # activity_csv = os.path.join(activity_dir, config.final_data_dir, config.resultat_csv_filename)

    if not os.path.exists(activity_dir):
        raise FileNotFoundError(f"Le dossier de l'activité '{activity}' n'existe pas dans {config.activity_dir}")
    
    if not os.path.exists(source_data_activity_dir):
        raise FileNotFoundError(f"Le dossier 'source_data' n'existe pas dans {activity_dir}")
    
    if not os.path.exists(synthesis_data_dir):
        os.makedirs(synthesis_data_dir)

    if not os.path.exists(synthesis_csv):
        with open(synthesis_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Élève', 'Classe', 'Groupe'])
    
    if not os.path.exists(synthesis_json):
        with open(synthesis_json, 'w') as f:
            json.dump({
                "tags": {},
                "exercises": {},
                "students": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "synthesized_activities": []
                }
            }, f, indent=2)
    
    update_synthesis_files(synthesis_csv, synthesis_json, activity_json, activity)

if __name__ == "__main__":
    main()

# Utilisation de la fonction
# update_synthesis('data/synthesis.csv', 'data/synthesis.json', 'data/Activités/1-Calcul_littéral/final_data/resultat.csv', 'data/Activités/1-Calcul_littéral/final_data/resultat.json')
