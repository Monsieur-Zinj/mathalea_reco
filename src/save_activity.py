import os
import sys
from src.config import Config
from src.db.data_processor import DataProcessor, URLProcessor, DataAnalyzer
from src.db.json_utils import generate_json_data, update_or_create_json
from src.db.data_processing import process_and_analyze_data
from src.user_interaction import get_optional_tags

from src.models.url_model import UrlParamsModel

def main():
    # Check if an activity is provided as a command-line argument
    if len(sys.argv) > 1:
        activity = sys.argv[1]
    else:
        activity = None

    config = Config()

    # If an activity was provided as an argument, override the config
    if activity:
        config.activity = activity

    activity_dir = os.path.join(config.activity_dir, config.activity)
    source_data_dir = os.path.join(activity_dir, "source_data")

    if not os.path.exists(activity_dir):
        print(f"Error: Activity folder '{config.activity}' does not exist in {config.activity_dir}")
        sys.exit(1)

    if not os.path.exists(source_data_dir):
        print(f"Error: 'source_data' folder does not exist in {activity_dir}")
        sys.exit(1)

    print(f"Processing data for activity: {config.activity}")

    try:
        final_df, url_infos = process_and_analyze_data(source_data_dir, config)
        

        # Get optional tags from user
        print("Enter optional tags for the activity:")
        tags = get_optional_tags()

        # Generate JSON data

        url_infos = [UrlParamsModel(**url_info) for url_info in url_infos]
        json_data = generate_json_data(final_df, tags, url_infos)

        # Prepare output directory
        output_dir = os.path.join(config.activity_dir, config.activity, config.final_data_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Save CSV
        csv_output_path = os.path.join(output_dir, config.resultat_csv_filename)
        final_df.to_csv(csv_output_path, index=False)

        # Save or update JSON
        json_output_path = os.path.join(output_dir, f"{os.path.splitext(config.resultat_csv_filename)[0]}.json")
        update_or_create_json(json_output_path, json_data)

        print(f"Data successfully processed and saved to:")
        print(f"CSV: {csv_output_path}")
        print(f"JSON: {json_output_path}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
