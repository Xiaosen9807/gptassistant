import os
import openai
import GPTlib as f

def completion():

    openai.api_key = os.getenv("OPENAI_API_KEY")

    filename = '../comments/messages.txt'

    prompt = f.extract_last_prompt_and_answer(filename)

    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt,
      temperature=0.45,
      max_tokens=3749,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    f.add_response_to_file(filename, response)

if __name__ == '__main__':
    completion()