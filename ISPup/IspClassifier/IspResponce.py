from typing import Optional
from pydantic import BaseModel
import logging

logging.getLogger(__name__)


class IspResponse(BaseModel):
    hash_value: str
    client_refer_key: str
    seconds_elapsed: Optional[int]

    def update_stamp(self, new_stamp):
        logging.info(f"Receieved new stamp update of {new_stamp}")
        self.seconds_elapsed = int(new_stamp)

    def get_stamp(self):
        return int(self.seconds_elapsed)
