#!/usr/bin/env python

import argparse
import GPTlib as f

# Define command-line arguments 
parser = argparse.ArgumentParser(description="This is a python script to run specific functions from it in the CLI")
parser.add_argument("--function",
                    help = "Name of the function to be executed")

parser.add_argument("-fn", "--filename",
                    default = "../GPT/document_scan.txt",
                    help = "Filename used to scan the documents")

parser.add_argument("-fc", "--filename_completion",
                    default = '../GPT/messages.txt',
                    help = "Filename used for completion")
                    
parser.add_argument("-fs", "--filename_system",
                    default = '../GPT/system.txt',
                    help = "Filename used for system messages")
parser.add_argument("-fw", "--filename_word",
                    default = '../GPT/test.docx',
                    help = "Filename of a word document")

parser.add_argument("-s", "--server",
                    default = 'ollama',
                    help = "The server name where the request is sent to. The default is 'ollama', meaning it is sent to a local server. Other option is 'openai'.")

# Parse the command-line arguments
args = parser.parse_args()

def word(filename_promtps = args.filename_completion, filename_word = args.filename_word, filename_system = args.filename_system):
    
    prompt = f.extract_word_text(filename_word)
    print(prompt)
    system = f.read_txt_file(filename_system)
    print(system)
    response = f.client_completion_stream(prompt, system)
    f.add_response_to_file(filename_promtps, response)
    
    

def completion(filename_promtps = args.filename_completion, 
               filename_system = args.filename_system, 
               server = args.server):

    prompt = f.extract_last_prompt_and_answer(filename_promtps)
    system = f.read_txt_file(filename_system)
    
    if server == 'ollama':
        response = f.client_completion_stream(prompt, system)
    elif server == 'openai':
        response = f.completion(prompt, system)
    else:
        response = f'\n ERROR: the selected server {server} is not existing among the posible choices'
        print(response)
    
    f.add_response_to_file(filename_promtps, response)

def highlight(filename = args.filename):
    
    filename, section_list, instructions = f.extract_instructions(filename)
    f.pdf_highlight(filename, section_list, instructions)

# Map the command-line argument with the functions
function_dict = {
    'word' : word,
    'completion' : completion,
    'highlight' : highlight
    }

# Execute the function
function_dict.get(args.function)()