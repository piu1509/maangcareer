
import threading
import time
 

def my_background_task():
    while True:
        from courseManagement.helpers import send_mail_for_all_student
        send_mail_for_all_student()
        print("Task is running")
        time.sleep(86400)