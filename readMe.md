
---

# Flashcard Website Project

## Description

This project is a simple flashcard web application for language learning. It displays flashcards showing words in Norwegian and their English translations. Users can view a random word and its translation by clicking on the flashcard or using the 'Next Word' button. The words and translations are fetched from a JSON file, which can be updated with the latest words by running a Python script.

## Features

- Display flashcards with Norwegian words and their English translations.
- Toggle between the Norwegian word and the English translation by clicking the flashcard.
- Fetch a new random word and its translation by clicking the 'Next Word' button.
- Update the list of words and translations through a Python script.

## Prerequisites

- Python 3
- A modern web browser

## Setup & Installation

1. Clone the repository or download the project files.
2. Navigate to the project directory.

## Running the Project

### Starting the Server

Run the following command to start a simple HTTP server:

```bash
python3 -m http.server
```

### Accessing the Flashcard Website

After starting the server, open your web browser and go to:

```
http://localhost:8000/index.html
```

### Updating the List of Words

To update the list of words and their translations:

1. Ensure you have the necessary credentials and environment variables set for accessing the Duolingo API.
2. Add any words you want to ignore to the list at the start of main
3. Run the Python script:

```bash
python3 main.py
```

4. Update any mistranslated words in the json file

This script fetches the latest words from Duolingo, translates them, and updates the `words_translations.json` file used by the flashcard website.

## Usage

- Once the server is running and the website is accessed, you will see a flashcard showing a Norwegian word.
- Click the flashcard to view its English translation.
- Click the 'Next Word' button to fetch a new word.
- Click the flashcard again to toggle back to the Norwegian word.

## Contributing

Contributions to the Flashcard Website Project are welcome. Please feel free to fork the repository, make improvements or add new features, and submit a pull request.
---