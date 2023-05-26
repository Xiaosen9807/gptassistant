import fitz, openai, os


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
        file_obj.write(f"\nanswer:\n{response[0]}\ntokens used: {response[1]}\n")
        print(response[0])

def completion(prompt):

    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    Q, A = get_QA_lists(prompt)
        
    if len(Q)==0:
        print('no chat detected')
        
        response = openai.Completion.create(
          model="text-davinci-003",
          prompt=prompt,
          temperature=0.1,
          max_tokens=3000,
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
        
        response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': role, 'content': content} for role, content in zip(roles, R)],
        temperature=0,
        )
        return ['A: ' + response.choices[0].message.content.strip(), response.usage.total_tokens]

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