

import duolingo
import os
from dotenv import load_dotenv
import requests
import inspect
import json
import logging

words_to_ignore = ["det", "names", "en"]

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')

username = os.environ.get('DUOLINGO_USER')
password = os.environ.get('DUOLINGO_PASSWORD')
jwt = os.environ.get('DUOLINGO_JWT')    

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
        translated_text = input(f"What is the translation for {norwegian_word} (or type ignore): ")
        
        if translated_text.lower() != 'ignore':
            translations.append({'Norwegian': norwegian_word.title(), 'English': translated_text.title()})
        
        logging.debug("Translated: %s -> %s", norwegian_word, translated_text)

    for translation in translations:
        longging.info(translation)
    if len(translations) > 0:
        with open('words_translations.json', 'w', encoding='utf-8') as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

except Exception as e:
    logging.error("Error during translation process:", str(e))
    raise