from pipeline import Pipeline

def lambda_handler(event, context):
    try:
        pipeline = Pipeline()

        pipeline.run()

        return {
            "status": "success",
            "message": "ETL pipeline executed successfully"
        }
    except Exception as e:
        print(f"Error occurred in the ETL pipeline: {e}")
        return {
            "status": "error",
            "message": str(e)
        }