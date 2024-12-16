import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.etl.pipeline import Pipeline

if __name__ == '__main__':
    try:
        pipeline = Pipeline()
        pipeline.run()
        print('ETL pipeline executed successfully.')
    except Exception as e:
        print(f'Error occurred while running the pipeline: {e}')
