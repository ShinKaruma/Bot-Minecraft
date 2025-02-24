import json



def get_message( key):
        locale = "fr"
        with open('lang.json', 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
        return lang_data.get(locale, {}).get(key, lang_data["en-US"].get(key, "Message not found"))


if __name__ == "__main__":
      print(get_message("daily")["reward"])