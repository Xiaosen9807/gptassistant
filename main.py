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
                    help = "Filename used to scan the documents")

# Parse the command-line arguments
args = parser.parse_args()



def completion(filename = args.filename_completion):

    prompt = f.extract_last_prompt_and_answer(filename)
    
    response = f.completion(prompt)
    
    f.add_response_to_file(filename, response)

def highlight(filename = args.filename):
    
    filename, section_list, instructions = f.extract_instructions(filename)
    f.pdf_highlight(filename, section_list, instructions)

# Map the command-line argument with the functions
function_dict = {
    'completion' : completion,
    'highlight' : highlight
    }

# Execute the function
function_dict.get(args.function)()