import openai_secret_manager
import os

api_key = os.environ.get('OPENAI_API_KEY')

# Fetch your OpenAI API key
secrets = openai_secret_manager.get_secret("openai")
api_key = secrets[api_key]

# Initialize the OpenAI API client
import openai
openai.api_key = api_key
