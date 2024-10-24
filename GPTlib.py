import fitz, openai, os, sys, requests, json, time
import base64
from openai import OpenAI
from docx import Document
from docx.text.paragraph import Paragraph
from docx.document import Document
from docx.table import _Cell, Table
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
import docx



def load_docx(file_path):
    try:
        return Document(file_path)
    except Exception as e:
        print(f"Error loading document: {e}")
        return None
        
        
def extract_word_text(filename):
    doc = docx.Document(filename)
    full_text = []
    for block in iter_block_items(doc):
        full_text.append(block.text)
    return '\n'.join(full_text)
    



def iter_block_items(parent):
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            table = Table(child, parent)
            for row in table.rows:
                for cell in row.cells:
                    yield from iter_block_items(cell)
    
    
def send_request(url, **kwargs):
  """Sends a chat message to the specified API endpoint.

  Args:
    url: The URL of the API endpoint.
    **kwargs: Keyword arguments to customize the request. 
              Accepted keys: 'model', 'messages' (list of dictionaries).

  Returns:
    The server's response as a JSON object, or None if an error occurred.
  """
  try:
    response = requests.post(url, json=kwargs)
    response.raise_for_status()  # Raise an exception for bad status codes
    # create variables to collect the stream of chunks
    collected_chunks = []
    collected_messages = ''
    
    ollama_url=os.environ.get("OLLAMA_URL")
    # iterate through the stream of events
    print(ollama_url)
    if url==f'{ollama_url}api/chat':
        print('A:', end="")
        for chunk in response.iter_lines():
            if chunk:
                json_response = json.loads(chunk.decode('utf-8'))
                chunk_message = json_response["message"]['content']
                #time.sleep(0.1)
                print(chunk_message, end="", flush=True)
                collected_messages = collected_messages + chunk_message  # save the message
        
        return collected_messages, json_response['prompt_eval_count'], json_response['prompt_eval_count'] / json_response['total_duration'] * 10**9
    else:
        print('\n', end="")
        for chunk in response.iter_lines():
            if chunk:
                json_response = json.loads(chunk.decode('utf-8'))
                chunk_message = json_response["response"]
                time.sleep(0.1)
                print(chunk_message, end="", flush=True)
                collected_messages = collected_messages + chunk_message  # save the message
        return collected_messages, json_response['prompt_eval_count'], json_response['prompt_eval_count'] / json_response['total_duration'] * 10**9
        
  except requests.exceptions.RequestException as e:
    print(f"Error sending message: {e}")
    return None
    
def extract_last_prompt_and_answer(filename):
    """Function to extract the content of the last prompt and answer from a text file"""

    # open the file in read mode
    with open(filename, 'r', encoding='utf-8') as f:
        # create an empty list to store the lines
        lines = []
        # iterate over each line in the file
        for line in f:
            # append each line to the list
            lines.append(line)
        
        ia = - 1 # initial index for the answer id
        for i, line in enumerate(reversed(lines)):
            if line.startswith('answer:'):
                ia = i
            if line.startswith('prompt:'):
                
                lines[len(lines) - i - 1] = line.replace('prompt:', '')
                
                break
        prompt = ''.join(lines[len(lines) - i - 1:len(lines) - ia - 1])
        print(f"prompt to work on:{prompt}")
        return prompt

def get_QA_lists(prompt):
    A_list = []
    Q_list = []
    cursor = ''
    lines = prompt.split('\n')
    for line in lines:
        if line.startswith('Q:'):
            Q_list.append(line.replace('Q:', ''))
            cursor = 'Q'
        elif line.startswith('A:'):
            A_list.append(line.replace('A:', ''))
            cursor = 'A'
        elif cursor=='A':
            A_list[-1] += '\n' + line
        elif cursor=='Q':
            Q_list[-1] += '\n' + line
    
    return Q_list, A_list
    
    
def add_response_to_file(filename, response):
    with open(filename, 'a', encoding='utf-8') as file_obj:
        # file_obj.write(f"\nanswer:\n{response[0]}\ntokens used: {response[1]}\n")
        # print(response[0])
        file_obj.write(f"\nanswer:\n{response} \n")

def completion(prompt, system):
    
    client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
    )
    
    Q, A = get_QA_lists(prompt)
        
    if len(Q)==0:
        print('no chat detected')
        
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.1,
          max_tokens=10000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        
        return [response.choices[0].text.strip(), response.usage.total_tokens]
    
    else:
        R = [None]*(len(Q)+len(A))
        roles = [None]*(len(Q)+len(A))
        R[0::2] = Q
        R[1::2] = A
        roles[0::2] = ['user' for i in range(len(Q))]
        roles[1::2] = ['assistant'  for i in range(len(A))]
        
        response = client.chat.completions.create(
        model='gpt-4o',
        messages = [ {'role': 'system', 'content': system},
         *[{'role': role, 'content': content} for role, content in zip(roles, R)]],
        temperature=0,
        )
        print(response.choices[0].message.content.strip())
        return ''.join(['A: ' + response.choices[0].message.content.strip(), f', {response.usage.total_tokens}'])
        

def client_completion(prompt, system):

    
    Q, A = get_QA_lists(prompt)
        
    if len(Q)==0:
        print('no chat detected')
        
        response = client.openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.1,
          max_tokens=10000,
          top_p=1,
          frequency_penalty=0,
          presence_penalty=0
        )
        
        return [response.choices[0].text.strip(), response.usage.total_tokens]
    
    else:
        R = [None]*(len(Q)+len(A))
        roles = [None]*(len(Q)+len(A))
        R[0::2] = Q
        R[1::2] = A
        roles[0::2] = ['user' for i in range(len(Q))]
        roles[1::2] = ['assistant'  for i in range(len(A))]
        model="gemma2_context"
        
        response = client.chat.completions.create(
        model=model,
        messages=[ {'role': 'system', 'content': system},
        *[{'role': role, 'content': content} for role, content in zip(roles, R)]],
        temperature=0,
        )
        print(response)
        return ['A: ' + response.choices[0].message.content.strip() + f'\nmodel used: {model}', response.usage.total_tokens]
        
def client_completion_stream(prompt, system):
    ollama_url=os.environ.get("OLLAMA_URL")
    Q, A = get_QA_lists(prompt)
    model="gemma2"
    
    if len(Q)==0:
        print('no chat detected')
        response, tokens, speed = send_request(f'{ollama_url}api/generate', 
          model=model,
          prompt=prompt,
          system = system,
          options = {'num_ctx':100000, 'temperature':0},
          keep_alive = 20
        )
        
        return ''.join(response) + f'\nmodel used: {model}\ntokens used: {tokens} \nspeed [tokens/s]: {speed}'
    
    else:
          
        R = [None]*(len(Q)+len(A))
        roles = [None]*(len(Q)+len(A))
        R[0::2] = Q
        R[1::2] = A
        roles[0::2] = ['user' for i in range(len(Q))]
        roles[1::2] = ['assistant'  for i in range(len(A))]
        
        response, tokens, speed = send_request(f'{ollama_url}api/chat', 
                    model = model,
                    options = {'num_ctx':100000, 'temperature':0},
                    messages = [ {'role': 'system', 'content': system},
         *[{'role': role, 'content': content} for role, content in zip(roles, R)]]
        )
        
        return 'A: ' + ''.join(response) + f'\nmodel used: {model}\ntokens used: {tokens} \nspeed [tokens/s]: {speed}'
        

def get_words(text, start, end):
    start_idx = text.find(start)
    end_idx = text.find(end)
    
    if start_idx == -1 or end_idx == -1:
        return False
    else:
        return text[start_idx+len(start):end_idx]
    

def pdf_highlight(filename, section_list, checks):
    section_list = section_list.split(', ')
    print(section_list)
    doc = fitz.open(filename)
    text = ''
    for page in doc:
        text += page.get_text().replace('\n', ' ')
        
    for start_word, end_word in zip(section_list[0:-1], section_list[1:]):
        section = get_words(text, start_word, end_word)
        
        if section == False:
            print("No sections found")
        else:
            print(f"Section {start_word} \n\n" + section)
            response = completion("\n" + checks + "\n" + section)
            print(f"\ncorrections: \n" + response.choices[0].text.strip() + '\n')
            
            with open(filename[0:-3]+'txt', 'a', encoding='utf-8') as file_obj:
                file_obj.write(f"Section {start_word} \n\n")
                file_obj.write(response.choices[0].text.strip() + '\n')


def extract_instructions(filename):
  with open(filename, 'r') as f:
    data = f.readlines()
    filename = ''
    section_list = ''
    instructions = ''
    for line in data:
      if line.startswith('filename'):
        filename = line.replace('filename:','').strip()
      elif line.startswith('section_list'):
        section_list = line.split(':')[1].strip()
      elif line.startswith('instructions'):
        instructions = line.split(':')[1].strip()
      else:
        instructions += "\n" + line.strip()
    print(filename)
    print(section_list)
    print(instructions)
    return filename, section_list, instructions
    
def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            
            return file.read()
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None