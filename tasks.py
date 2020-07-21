# from celery import shared_task
# import logging
import os

# logger = logging.getLogger(__name__)

# @shared_task
# def test_task():
#     command = "python /home/bootcamp/src/cli2/invenio-rdm-pure/invenio_rdm_pure/cli.py pages"
#     os.system(f"{command}  --pageStart=1 --pageEnd=2 --pageSize=1")
#     print("\n\nIN TEST_TASK !!!!!!!!!!\n\n")
#     return


from celery import shared_task


@shared_task
def add(x, y):
    command = "python /home/bootcamp/src/cli2/invenio-rdm-pure/invenio_rdm_pure/cli.py"
    os.system(f"{command} pages  --pageStart=1 --pageEnd=2 --pageSize=1")
    print("\n\ntest_task - test_task \n\n")
    return x + y

