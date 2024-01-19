

import duolingo
import os
from dotenv import load_dotenv
import requests
import inspect
import json
import logging
import deepl

words_to_ignore = ["det", "names", "en"]

load_dotenv()

os.system("python3 duolingo.py")

def translate_norwegian_to_english(text, auth_key):
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(text, target_lang="EN-US", source_lang="NB")
    return result.text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')

username = os.environ.get('DUOLINGO_USER')
password = os.environ.get('DUOLINGO_PASSWORD')
jwt = os.environ.get('DUOLINGO_JWT')   
auth_key = os.environ.get("auth_key") 

if username is None:
    raise Exception("Environment variable DUOLINGO_USERNAME is not set")

if jwt is None and password is None:
    raise Exception("Either DUOLINGO_PASSWORD or DUOLINGO_JWT must be set")

try:
  source = inspect.getsource(duolingo)
  new_source = source.replace('jwt=None', 'jwt')
  new_source = source.replace('self.jwt = None', ' ')
  exec(new_source, duolingo.__dict__)

  lingo  = duolingo.Duolingo(username, jwt=jwt)
except duolingo.DuolingoException as e:
    logging.error(f"Duolingo API returned an error: {e}")
except requests.exceptions.RequestException as e:
    logging.error(f"Request failed: {e}")
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
    
MyInfo = lingo.get_user_info()
logging.info(f"{username}: Info ID: {MyInfo['id']}")
logging.info(f"{username}: Info fullname: {MyInfo['fullname']}")

try:
    known_words = lingo.get_known_words('nb')
    logging.info(f"Known words fetched: {known_words}")

    
    try:
        with open('words_translations.json', 'r', encoding='utf-8') as file:
            existing_translations = json.load(file)
    except FileNotFoundError:
        existing_translations = []

    existing_norwegian_words = set([entry['Norwegian'].lower() for entry in existing_translations])
    logging.info(f"Already translated words: {existing_norwegian_words}")

    
    translations = []




    for norwegian_word in known_words:
        if norwegian_word in words_to_ignore:
            continue

        if norwegian_word.lower() in existing_norwegian_words:
            continue

        translated_text = translate_norwegian_to_english(norwegian_word, auth_key)
        
        translations.append({'Norwegian': norwegian_word.title(), 'English': translated_text.title()})
        
        logging.debug("Translated: %s -> %s", norwegian_word, translated_text)

    for translation in translations:
        logging.info(translation)
    if len(translations) > 0:
        with open('words_translations.json', 'a', encoding='utf-8') as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

except Exception as e:
    logging.error("Error during translation process:", str(e))
    raise


def fix_and_sort_json(file_path):
    # Read the existing data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Ensure all entries are in the correct format
    fixed_data = [
        {'Norwegian': entry['Norwegian'], 'English': entry['English']}
        for entry in data
        if isinstance(entry, dict) and 'Norwegian' in entry and 'English' in entry
    ]

    fixed_data.sort(key=lambda x: x['Norwegian'])

    data.extend(fixed_data)

    seen = set()
    unique_data = []
    for entry in data:
        identifier = (entry['Norwegian'], entry['English'])
        if identifier not in seen:
            seen.add(identifier)
            unique_data.append(entry)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(unique_data, file, indent=4, ensure_ascii=False)

# Usage
file_path = 'words_translations.json'
fix_and_sort_json(file_path)