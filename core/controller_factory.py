"""
controller_factory.py
- config.TV_TYPE에 따라 알맞은 TV 컨트롤러 객체를 생성하여 반환
"""
from config import config
from core.controllers.tizen_controller import TizenTVController
from core.controllers.lg_controller import LGTVController

def get_tv_controller():
    if config.TV_TYPE == "lg":
        print("[Factory] LG webOS TV Controller 선택됨")
        return LGTVController()
    elif config.TV_TYPE == "tizen":
        print("[Factory] 삼성 Tizen TV Controller 선택됨")
        return TizenTVController()
    else:
        raise ValueError(f"지원하지 않는 TV_TYPE입니다: {config.TV_TYPE}")