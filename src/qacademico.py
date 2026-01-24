import re
import requests

from src.models.coeficiente import Coeficiente
from .models import (
    Disciplina,
    Matriz,
    Usuario,
    HorarioItem,
    HorarioDiaItem,
    HorarioPeriodoItem,
    TurnoPeriodo,
    PeriodoLetivo,
    BoletimItem,
)
from bs4 import BeautifulSoup
from pydantic import TypeAdapter


class QAcademico:
    BASE_URL = "https://antigo.qacademico.ifce.edu.br"
    __REGEX_RSA = re.compile(r'new RSAKeyPair\(.*"(\w+)",.*"(\w+)"', re.DOTALL)
    API_URL = f"{BASE_URL}/webapp/api"
    __disciplinas_ta = TypeAdapter(list[Disciplina])
    __periodos_ta = TypeAdapter(list[PeriodoLetivo])
    __boletim_ta = TypeAdapter(list[BoletimItem])

    def __init__(self) -> None:
        self.__session = requests.Session()
        self.__session.headers = {
            "Referer": f"{self.BASE_URL}/qacademico/index.asp?t=1001",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        }

    def __encrypt(self, input, exp_hex, mod_hex):
        n = int(mod_hex, 16)
        e = int(exp_hex, 16)

        key_size = (n.bit_length() + 7) // 8

        encoded = input.encode("utf-8")

        padded = encoded + (b"\x00" * (key_size - len(encoded)))

        m = int.from_bytes(padded, byteorder="little")

        encrypted = pow(m, e, n)
        return hex(encrypted)[2:]

    def login(self, matricula: str, senha: str):
        qaca_url = f"{self.BASE_URL}/qacademico"
        # só pra pegar os cookies iniciais mesmo
        self.__session.get(f"{qaca_url}/index.asp", params={"t": 1001})
        rsa_req = self.__session.get(
            f"{qaca_url}/lib/rsa/gerador_chaves_rsa.asp",
            params={"form": "frmLogin", "action": "/qacademico/lib/validalogin.asp"},
        )
        if not rsa_req.ok:
            return False

        if (search := self.__REGEX_RSA.search(rsa_req.text)) is None:
            return False
        exp, mod = search.groups()

        data = {
            "LOGIN": self.__encrypt(matricula, exp, mod),
            "SENHA": self.__encrypt(senha, exp, mod),
            "TIPO_USU": self.__encrypt("1", exp, mod),
            "SUbmit": self.__encrypt("OK", exp, mod),
        }

        self.__session.headers["Referer"] = f"{qaca_url}/index.asp?t=1001"
        res = self.__session.post(
            f"{qaca_url}/lib/validalogin.asp",
            data=data,
            allow_redirects=False,
        )

        return res.status_code == 302 and res.text.find("?t=2000") != -1

    def matriz(self) -> Matriz:
        req = self.__session.get(f"{self.API_URL}/matriz-curricular/minha-matriz")
        # TODO: Checkagem de requisição

        return Matriz.model_validate_json(req.text)

    def disciplinas(self, matriz: Matriz) -> list[Disciplina]:
        req = self.__session.get(
            f"{self.API_URL}/matriz-curricular/disciplinas",
            params={
                "idMatrizCurricular": matriz.id_matriz,
                "idHabilitacao": matriz.habilitacoes[0].id_habilitacao,
            },
        )

        return self.__disciplinas_ta.validate_json(req.text)

    def usuario(self) -> Usuario:
        req = self.__session.get(f"{self.API_URL}/autenticacao/usuario-autenticado")

        return Usuario.model_validate_json(req.text)

    def horarios(
        self, periodo: PeriodoLetivo | None = None
    ) -> dict[str, HorarioDiaItem] | None:
        params = {"t": 2010}
        if periodo is not None:
            params = {
                **params,
                "Exibir": "OK",
                "COD_MATRICULA": -1,
                "cmbanos": periodo.ano,
                "cmbperiodos": periodo.periodo,
            }
        req = self.__session.get(f"{self.BASE_URL}/qacademico/index.asp", params=params)
        if not req.ok:
            return None
        doc = BeautifulSoup(req.text, "html.parser")
        return self.__horarios(doc)

    def __horarios(self, doc: BeautifulSoup) -> dict[str, HorarioDiaItem]:
        table = doc.select_one("table.conteudoTitulo + br + table")
        assert table is not None
        lines = table.select("tr")
        titles = [x.text.strip() for x in lines[0].select("font")]
        data = {x: HorarioDiaItem(items={}) for x in titles[1:]}
        for line in table.select("tr")[1:]:
            cols = line.select("td font")
            time = TurnoPeriodo(cols[0].text.strip()).name
            del cols[0]
            for i in range(0, len(cols)):
                key = titles[i + 1]
                data[key].items[time] = None
                col = cols[i]
                elemMateria = col.select_one("div:has(+br)")
                elemSala = col.select_one("div + br + div:has(+br)")
                if (
                    len(col.text.strip()) == 0
                    or elemMateria is None
                    or elemSala is None
                ):
                    continue
                cadeira = HorarioItem(
                    nome=str(elemMateria["title"]), sigla=elemMateria.text.strip()
                )
                sala = HorarioItem(
                    nome=str(elemSala["title"]), sigla=elemSala.text.strip()
                )
                data[key].items[time] = HorarioPeriodoItem(cadeira=cadeira, sala=sala)
        return data

    def periodos_letivos(self) -> list[PeriodoLetivo] | None:
        req = self.__session.get(f"{self.API_URL}/boletim/periodos-letivos")
        if not req.ok:
            return None

        return self.__periodos_ta.validate_json(req.text)

    def boletim(self, periodo: PeriodoLetivo) -> list[BoletimItem] | None:
        req = self.__session.get(
            f"{self.API_URL}/boletim/disciplinas",
            params=periodo.model_dump(by_alias=True),
        )
        if not req.ok:
            return None

        return self.__boletim_ta.validate_json(req.text)

    def coeficiente(self) -> Coeficiente | None:
        req = self.__session.get(f"{self.API_URL}/dashboard/aluno/grafico-rendimento")
        if not req.ok:
            return None

        return Coeficiente.model_validate_json(req.text, by_alias=True)
