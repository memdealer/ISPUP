import logging
import time
from dataclasses import dataclass

import telebot

logging.getLogger(__name__)


@dataclass
class Tinker:
    ISP_LIST: list
    ALERT_THRESHOLD: int
    __tg_api_token__: str
    __tg_api_notify_chat: int
    __ALERT_LIST__ = []

    def __post_init__(self):
        logging.info("Spawned Tinker."
                     f"Current ISPs {self.ISP_LIST} ")
        logging.info("Start polling")

    @dataclass
    class AlertClassifier:
        client_refer_key: str
        alert_started_at: int
        __tg_api_token__: str
        __tg_notify_chat__: int

        @staticmethod
        def __convert_unix_to_human__(time_to_convert) -> str:

            return time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(time_to_convert))

        def __post_init__(self) -> None:
            logging.info(f"Spawned alert for: [{self.client_refer_key}], start time recorded: {self.alert_started_at}")
            self.bot = telebot.TeleBot(self.__tg_api_token__)
            start_alert_msg = f"""
👉 ACHTUNG! 👈
[ {self.client_refer_key} ]  has gone offline! 
When: {self.__convert_unix_to_human__(self.alert_started_at)}
            """
            logging.info(f"Telegram notify for [{self.client_refer_key}] on spawned")

            self.bot.send_message(self.__tg_notify_chat__, start_alert_msg)

        def dismiss_alarm(self, unix_time) -> None:
            stop_alert_msg = f"""
🦍⛑
[ {self.client_refer_key} ] is BACK online! 
Alert started: {self.__convert_unix_to_human__(self.alert_started_at)}
Alert resolved: {self.__convert_unix_to_human__(unix_time)}
Total time in downtime: {unix_time - self.alert_started_at} seconds.
            """
            logging.info(f"[{self.client_refer_key}] has been brought ONLINE, dismissing alarm via notify.")
            self.bot.send_message(self.__tg_notify_chat__, stop_alert_msg)

    def __add_to_alert_list__(self, client_refer_key) -> None:
        current_time = int(time.time())
        alert_obj = self.AlertClassifier(client_refer_key, current_time,
                                         self.__tg_api_token__, self.__tg_api_notify_chat)
        self.__ALERT_LIST__.append(alert_obj)

    def __delete_alert_from_list__(self, client_refer_key) -> None:
        current_time = int(time.time())
        for index, alert_object in enumerate(self.__ALERT_LIST__):
            if alert_object.client_refer_key == client_refer_key:
                alert_object.dismiss_alarm(current_time)
                logging.info(f"Deleting object with [{alert_object.client_refer_key}] from watchlist.")
                self.__ALERT_LIST__.pop(index)

    def __find_alert_in_alert_list__(self, obj) -> bool:
        for alert_object in self.__ALERT_LIST__:
            if obj.client_refer_key in alert_object.client_refer_key:
                logging.info(f"[{alert_object.client_refer_key}] as it is exist in the alert list")
                logging.info(self.__ALERT_LIST__)
                return True
        return False

    def operate_and_judge(self):
        current_stamp = int(time.time())
        for isp in self.ISP_LIST:
            if self.ALERT_THRESHOLD >= (current_stamp - isp.get_stamp()):
                logging.debug(f"--- TINKER CHECK --- [{isp.client_refer_key}] looks healthy")
                if self.__find_alert_in_alert_list__(isp) is True:
                    logging.info(f"[{isp.client_refer_key}] is back online!")
                    self.__delete_alert_from_list__(isp.client_refer_key)
            else:  # in case thing went offline, trigger alarm
                if self.__find_alert_in_alert_list__(isp) is True:
                    logging.debug(f"[{isp.client_refer_key}] has already been marked as offline & added to alert list")
                    logging.info(f"[{isp.client_refer_key}] current offline stats:"
                                 f" Expected to confirm it is alive within: {self.ALERT_THRESHOLD} seconds"
                                 f" Currently offline for: {int(time.time()) - isp.get_stamp()} seconds!")
                else:
                    logging.warning(f"[{isp.client_refer_key}] has not been seen within {self.ALERT_THRESHOLD} seconds!"
                                    f"[{isp.client_refer_key}]has gone offline, triggering alarm")
                    self.__add_to_alert_list__(isp.client_refer_key)
                    logging.info(f"[{isp.client_refer_key}] has been added to alert list.")
                    logging.info(f" Currently watched alerts: {self.__ALERT_LIST__}")
