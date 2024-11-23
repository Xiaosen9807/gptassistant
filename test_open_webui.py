import os
import open_webui as op

# Set the OpenAI API key
openAI_API = ''
# openai.api_key = os.getenv("OPENAI_API_KEY")

os.environ['OPENAI_API_KEY'] = openAI_API

print('This is a test for webui')

# Start the OpenWebUI server
op.serve()
# Then open the browser with localhost:8080
