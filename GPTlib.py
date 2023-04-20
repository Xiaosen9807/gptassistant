
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
        print(f"prompt to work on:{''.join(lines[len(lines) - i - 1:len(lines) - ia - 1])}")
        return ''.join(lines[len(lines) - i - 1:len(lines) - ia - 1])
    
def add_response_to_file(filename, response):
    with open(filename, 'a', encoding='utf-8') as file_obj:
        file_obj.write(f"\nanswer:\n{response.choices[0].text.strip()}\ntokens used: {response.usage.total_tokens}\n")
                