from multiprocessing.connection import Client
from multiprocessing.connection import Listener

# адрес сервера (процесса в руте) для исходящих
# запросов
daemon = ('localhost', 6000)
# адрес клиента (этого процесса) для входящих
# ответов от сервера
cli = ('localhost', 6001)

def send(request: dict) -> bool or dict:
    """
    Принимает словарь аргументов удалённого метода.
    Отправляет запрос, после чего открывет сокет
    и ждет на нем ответ от сервера.
    """
    with Client(daemon) as conn:
        conn.send(request)
    with Listener(cli) as listener:
        with listener.accept() as conn:
            try:
                return conn.recv()
            except EOFError:
                return False

def hello(name: str) -> send:
    """
    Формирует уникальный запрос и вызывает функцию
    send для его отправки.
    """
    return send({
        "method": "hello",
        "name": name
    })