from dataclasses import dataclass
import json
import os

@dataclass(init=True, frozen=True)
class Config:
    all_clients = dict()

    with open("Config.json") as config_file:
        json_data = json.load(config_file)

    global_time_window_seconds = int(os.environ["TIME_WINDOW_SECONDS"])
    global_telegram_chat_id = os.environ["TELEGRAM_NOTIFY_CHAT_ID"]
    all_clients = json_data["Clients"]
    tg_api_key = os.environ["TELEGRAM_API_KEY"]

