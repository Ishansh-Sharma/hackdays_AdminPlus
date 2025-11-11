import os
from gradio_client import Client,file
from dotenv import load_dotenv


load_dotenv()
HF_TOKEN = os.getenv("HuggingFace_API")
print("API key loaded")

#fuck bitch .. api load ho gyi .. ab dekho .. 
#time stamp - 11:22
#ts - 11:34 - made and upload sample form


from gradio_client import Client, handle_file
print("q")
client = Client("merterbak/DeepSeek-OCR-Demo",hf_token=HF_TOKEN)
result_image = client.predict(
	file_path=handle_file('/Users/ishanshsharma/HackAI/MLH/Filled_Sample_form.pdf'),
	api_name="/load_image"
)
print(result_image, type(result_image))


client = Client("merterbak/DeepSeek-OCR-Demo")
result_toggle = client.predict(
	task="📋 Markdown",
	api_name="/toggle_prompt"
)
print(result_toggle)

from gradio_client import Client, handle_file

client = Client("merterbak/DeepSeek-OCR-Demo")
result = client.predict(
	image=handle_file(f'{result_image}'),
	file_path=handle_file('/Users/ishanshsharma/HackAI/MLH/Filled_Sample_form.pdf'),
	mode="Gundam",
	task="📋 Markdown",
	custom_prompt="Hello!!",
	api_name="/run"
)
print(result)

#time stamp - 1:41
gemini_api_key = os.getenv("Gemini_api_key")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

prompt = ""

#time-stamp : 

#11:40 - error 1 
#/private/var/folders/n6/k0xps3cj28g9vpqkfkdql2_r0000gn/T/gradio/7bdc024256f2dff3ee59cff4754ab937aab5ddc3c33568cbe95c5d532d8ce4d2/image.webp



