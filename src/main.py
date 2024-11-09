from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.utils import get_eui_addr, get_token_addr

app = FastAPI()


@app.get("/")
def get_ip(eui64: str | None = None, token: str | None = None) -> str:
    try:
        if token:
            return get_token_addr(token, eui64)
        if eui64:
            return get_eui_addr(eui64)
    except ValueError as exc:
        raise RequestValidationError(str(exc)) from exc
    else:
        raise RequestValidationError("Must provide eui64 or token query parameter")
