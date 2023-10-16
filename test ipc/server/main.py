                   
from core import api
#import logger
from multiprocessing.connection import Listener
from multiprocessing.connection import Client

# адрес сервера (этого процесса) для входящих запросов
daemon = ('localhost', 6000)
# адрес клиента для исходящих ответов
cli = ('localhost', 6001)
with Listener(daemon) as listener:
    response = None
    while not response:
        request = None
        while not request:
            with listener.accept() as conn:
                request = conn.recv()
        if request["method"] == "connect":
            response = api.connect(request)
        elif request["method"] == "disconnect":
            response = api.disconnect(request)
        else:
            response = None
        if response:
          try:
            with Client(cli) as conn:
                conn.send(response)
          except ConnectionRefusedError as e:
              print(e)
          else:
            response = None