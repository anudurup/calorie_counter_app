from datetime import date
from datetime import datetime
import math

def get_todos(filepath='todo.txt'):
    with open(filepath, 'r') as file_local:
        todos_local = file_local.readlines()
    return todos_local


def write_todos(todos_local,filepath='todo.txt'):
    with open(filepath, 'w') as file_local:
        file_local.writelines(todos_local)

def create_weekly_tracker_pages():
    pass

def get_dayname():
    dt = datetime.now()
    day_name = dt.strftime('%A')
    return day_name
