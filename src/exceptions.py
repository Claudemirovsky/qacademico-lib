import re
from requests.models import Response


class QAcademicoError(Exception):
    pass


class LoginError(QAcademicoError):
    pass


class ApiError(QAcademicoError):
    BASE_URL_REGEX = re.compile(r"http[s]?://\S+?/")

    def __init__(self, type: str, response: Response):
        code = response.status_code
        url = self.BASE_URL_REGEX.sub("/", response.url)
        self.message = f"Falha ao obter {type}: HTTP {code} em {url}"
        super().__init__(self.message)
