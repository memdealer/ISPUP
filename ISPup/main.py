import logging
from time import time

from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every

from Config import Config
from IspClassifier import IspResponse
from IspClassifier import Tinker

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level="DEBUG")

ISP_LIST = []
app = FastAPI(debug=True)


tinker = Tinker(ISP_LIST, Config.global_time_window_seconds,
                Config.tg_api_key, Config.global_telegram_chat_id)


@app.on_event("startup")
@repeat_every(seconds=15)
def wrapper():
    tinker.operate_and_judge()


@app.post("/health_report")
async def isp_health_gatherer(isp_client: IspResponse, request: Request):
    found_client = list(
        filter(
            lambda isp: isp_client.hash_value == Config.all_clients[isp]["hash_value"],
            Config.all_clients
        )
    )

    if len(found_client):
        if isp_client.client_refer_key not in [k.client_refer_key for k in ISP_LIST]:
            logging.info(f"[{isp_client.client_refer_key}] not present in watch list, adding it.")
            isp_client.update_stamp(
                time()
            )
            ISP_LIST.append(isp_client)
            return "<p> Added! </p>"
        else:
            logging.info(f"[{isp_client.client_refer_key}] received keep-alive ack!")
            found_client = list(
                filter(
                    lambda isp: isp_client.hash_value == isp.hash_value,
                    ISP_LIST
                )
            )
            found_client[0].update_stamp(
                time()
            )
            return "<p> Ack </p>"
    else:
        logging.warning(f"IP: {request.client.host} {isp_client.hash_value, isp_client.client_refer_key}"
                        f" -- has not been declared in the list of allowed ISPs")
        return "<p> Go away! </p>"
