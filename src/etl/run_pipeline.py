from pipeline import Pipeline

if __name__ == '__main__':
    try:
        pipeline = Pipeline()
        pipeline.run()
        print('ETL pipeline executed successfully.')
    except Exception as e:
        print(f'Error occurred while running the pipeline: {e}')