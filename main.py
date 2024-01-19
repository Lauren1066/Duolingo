

import duolingo
import os
from dotenv import load_dotenv
import requests
import inspect
import json
import logging
import deepl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')
load_dotenv()
os.system("python3 duolingo.py")
auth_key = os.environ.get("auth_key") 
get_vocab = True
words_to_ignore = [
    "names", 
    "olivia", 
    "thomas",
    "lisa",
    "mari",
    "marius",
    "anders",
    "liv",
    "maria",
    "katja"
]

known_mispelled_words = [
    "gar",
    "brodet",
    "brod",
    "servitor",
    "servitoren",
    "laerer",
    "sosteren",
    "soster",
    "ol",
    "vaer",
    "sonnen",
    "hoy"
]


def login():
    username = os.environ.get('DUOLINGO_USER')
    password = os.environ.get('DUOLINGO_PASSWORD')
    jwt = os.environ.get('DUOLINGO_JWT')   
    

    if username is None:
        raise Exception("Environment variable DUOLINGO_USER is not set")

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
    return lingo


def translate_norwegian_to_english(text, auth_key):
    translator = deepl.Translator(auth_key)
    result = translator.translate_text(text, target_lang="EN-US", source_lang="NB")
    return result.text



def get_user_info(lingo):
    username = os.environ.get('DUOLINGO_USER')
    MyInfo = lingo.get_user_info()
    logging.info(f"{username}: Info ID: {MyInfo['id']}")
    logging.info(f"{username}: Info fullname: {MyInfo['fullname']}")

def is_norwegian_word_in_json(norwegian_word):
    file_path = 'words_translations.json'
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words_data = json.load(file)

        norwegian_word_normalized = norwegian_word.lower()
        
        for entry in words_data:
            if 'Norwegian' in entry and entry['Norwegian'].lower() == norwegian_word_normalized:
                return True  

        return False
    except FileNotFoundError:
        logging.error(f"The file {file_path} was not found.")
        return False
    except json.JSONDecodeError:
        logging.error(f"Error decoding the JSON from the file {file_path}.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False

    
def handle_vocab(lingo):
    if get_vocab:
        vocab = lingo.get_vocabulary()
        vocab_overview = vocab['vocab_overview']
        vocab_words = [entry['normalized_string'] for entry in vocab_overview]
        
        translations = []  
        translations_file = 'words_translations.json'

        for word in vocab_words:
            word_lower = word.lower()
            if any(mispelled_word in word_lower for mispelled_word in known_mispelled_words) or is_norwegian_word_in_json(word) or word in words_to_ignore:
                continue
            english_translation = translate_norwegian_to_english(word, auth_key)
            translation_entry = {"Norwegian": word, "English": english_translation}
            translations.append(translation_entry)
        append_data_to_json(translations_file, translations)


def append_data_to_json(file_path, data_list):
    if not all(isinstance(item, dict) and 'Norwegian' in item and 'English' in item for item in data_list):
        raise ValueError("Data must be a list of dictionaries, each with 'Norwegian' and 'English' keys")

    existing_data = []

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            try:
                existing_data = json.load(file)
                if not isinstance(existing_data, list):
                    raise ValueError("The JSON file should contain a list of translations")
            except json.JSONDecodeError:
                logging.error(f"The file {file_path} is not a valid JSON file or is empty. A new file will be created.")
    
    for item in data_list:
        existing_data.append(item)

    with open(file_path, 'w') as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)

    logging.info(f"Data appended successfully to {file_path}")


def handle_known_words(lingo):
    try:
        known_words = lingo.get_known_words('nb')
        logging.info(f"Known words fetched: {known_words}")

        try:
            with open('words_translations.json', 'r', encoding='utf-8') as file:
                existing_translations = json.load(file)
        except FileNotFoundError:
            existing_translations = []
        except json.JSONDecodeError:
            logging.error("Error decoding the JSON file.")
            existing_translations = []

        existing_norwegian_words = set([entry['Norwegian'].lower() for entry in existing_translations])
        logging.info(f"Already translated words: {existing_norwegian_words}")

        translations = []

        for norwegian_word in known_words:
            if norwegian_word in words_to_ignore:
                continue
            word_lower = norwegian_word.lower()
            if any(mispelled_word in word_lower for mispelled_word in known_mispelled_words):
                 continue

            if is_norwegian_word_in_json(norwegian_word):
                continue

            try:
                translated_text = translate_norwegian_to_english(norwegian_word, auth_key)
                translations.append({'Norwegian': norwegian_word.title(), 'English': translated_text.title()})
                logging.debug(f"Translated: {norwegian_word} -> {translated_text}")
            except Exception as e:
                logging.error(f"Error during the translation of {norwegian_word}: {str(e)}")

        for translation in translations:
            logging.info(translation)

        if len(translations) > 0:
            append_data_to_json('words_translations.json', translations)

    except Exception as e:
        logging.error(f"Error during the known words handling process: {str(e)}")
        raise



def fix_and_sort_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    fixed_data = sorted(
        (
            {
                'Norwegian': entry['Norwegian'].title() if 'Norwegian' in entry else '',
                'English': entry['English'].title() if 'English' in entry else ''
            }
            for entry in data if isinstance(entry, dict) and 'Norwegian' in entry and 'English' in entry
        ),
        key=lambda x: x['Norwegian']
    )

    seen = set()
    unique_data = []
    for entry in fixed_data:
        identifier = (entry['Norwegian'], entry['English'])
        if identifier not in seen:
            seen.add(identifier)
            unique_data.append(entry)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(unique_data, file, indent=4, ensure_ascii=False)  
    logging.info(f"Data in {file_path} is fixed, sorted, and duplicates are removed.")




def main():
    load_dotenv()
    get_vocab = True 

    lingo = login()
    if lingo is None:
        logging.error("Failed to login to Duolingo.")
        return

    get_user_info(lingo)

    if get_vocab:
        handle_vocab(lingo)

    handle_known_words(lingo)

    file_path = 'words_translations.json'
    fix_and_sort_json(file_path)

    logging.info("Script execution completed successfully.")

if __name__ == '__main__':
    main()
