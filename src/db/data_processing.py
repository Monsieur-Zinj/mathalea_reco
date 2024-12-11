from src.db.data_processor import DataProcessor, URLProcessor, DataAnalyzer

def process_and_analyze_data(source_data_dir, config):
    # Initialize DataProcessor
    data_processor = DataProcessor(source_data_dir, config)

    # Process input files
    print("Processing data files...")
    df_res = data_processor.process_res()
    # df_meta = data_processor.process_meta()
    df_groupe = data_processor.process_eleve_groupe()

    # Process URL
    with open(data_processor._get_path(config.url_filename)) as f:
        url = URLProcessor.extract_url_from_html(f.read())
    url_dict = URLProcessor.parse_url(url)
    print(f"URL dictionary: {url_dict}")

    # Analyze data
    analyzer = DataAnalyzer(df_res, df_groupe, url_dict)
    return analyzer.prepare_final_dataframe(), url_dict
