

import duolingo
import os
from dotenv import load_dotenv
import requests
import inspect
import json
import googletrans
import logging

words_to_ignore = ["det", "names", "en"]

load_dotenv()

translator = googletrans.Translator()

load_dotenv() 

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
    print(f"Duolingo API returned an error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    
print("---InfoPart---Start---")
streak_info = lingo.get_streak_info()
print(f"{username}: get_streak_info for {streak_info}")
MyInfo = lingo.get_user_info()
print(f"{username}: Info ID: {MyInfo['id']}")
print(f"{username}: Info fullname: {MyInfo['fullname']}")
print(f"{username}: Info location: {MyInfo['location']}")
print(f"{username}: Info contribution_points: {MyInfo['contribution_points']}")
print(f"{username}: Info created: {MyInfo['created'].strip()}")
print(f"{username}: Info learning_language_string: {MyInfo['learning_language_string']}")
print(f"{username}: streak_freeze: {lingo.__dict__['user_data'].__dict__['tracking_properties']['num_item_streak_freeze']}")
print(f"{username}: rupee_wager: {lingo.__dict__['user_data'].__dict__['tracking_properties']['has_item_rupee_wager']}")
user_data_resp = lingo.get_data_by_user_id()
print(f"{username}: Info lingots: {user_data_resp['lingots']}")
print(f"{username}: Info totalXp: {user_data_resp['totalXp']}")
print(f"{username}: Info monthlyXp: {user_data_resp['monthlyXp']}")
print(f"{username}: Info weeklyXp: {user_data_resp['weeklyXp']}")
print(f"{username}: Info gems: {user_data_resp['gems']}")
print(f"{username}: Info currentCourse.crowns: {user_data_resp['currentCourse']['crowns']}")


try:
    known_words = lingo.get_known_words('nb')
    print("Known words fetched:", known_words)
    
    try:
        with open('words_translations.json', 'r', encoding='utf-8') as file:
            existing_translations = json.load(file)
    except FileNotFoundError:
        existing_translations = []

    existing_norwegian_words = set([entry['Norwegian'].lower() for entry in existing_translations])
    print("Already translated words:", existing_norwegian_words)

    
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
        print(translation)
    if len(translations) > 0:
        with open('words_translations.json', 'w', encoding='utf-8') as file:
            json.dump(translations, file, ensure_ascii=False, indent=4)

except Exception as e:
    logging.error("Error during translation process:", str(e))
    raise