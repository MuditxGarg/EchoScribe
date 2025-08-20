import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    """ Bot Configuration """

    az_openai_key=os.getenv("AZURE_OPENAI_API_KEY")
    az_open_ai_endpoint_name=os.getenv("AZURE_OPENAI_ENDPOINT_NAME")
    az_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    model_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")