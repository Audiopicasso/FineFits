from app.config import get_settings


def get_app_name() -> str:
    return get_settings().app_name


def get_mobile_app_scheme() -> str:
    return get_settings().mobile_app_scheme
