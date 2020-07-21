from tasks import add
from pprint import pprint
from celery import Celery

result = add.delay(4, 5)
print("")
pprint(result)
print("")
pprint(vars(result))

# ----------

# app1 = Celery(broker="amqp://")
# add.app is app1
# print(app1)
# pprint(vars(app1))
