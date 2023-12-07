import os
import openai
from dotenv import load_dotenv
from prompt import PROMPT as BASE_PROMPT


load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


GPT_MODEL = "gpt-4-1106-preview"
LECTURE_DIR = "./"
INPUT_FILE = os.path.join(LECTURE_DIR, "ryu_custom.txt")
OUTPUT_FILE = os.path.join("./", "result.txt")
PROMPT = BASE_PROMPT


class AnswerGenerator:
    def __init__(self, api_key, model=GPT_MODEL, prompt=PROMPT):
        openai.api_key = api_key
        self.model = model
        self.prompt = prompt

    def get_answer(self, subtitle, question):
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": subtitle},
                    {"role": "user", "content": question},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error occurred: {e}")
            return ""


def read_file(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return ""


def write_file(file_path, content):
    try:
        with open(file_path, "w") as f:
            f.write(content)
    except Exception as e:
        print(f"Error occurred while writing to {file_path}: {e}")


def task():
    subtitle = read_file(INPUT_FILE)
    question = "쓰레드란 무엇인가요?"
    if subtitle:
        answer_generator = AnswerGenerator(api_key=API_KEY)
        response = answer_generator.get_answer(subtitle, question)
        if response:
            write_file(OUTPUT_FILE, response)
            # print(response)
            return response


if __name__ == "__main__":
    task()
