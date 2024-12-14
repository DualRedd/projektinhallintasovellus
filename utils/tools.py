from sqlalchemy import Row
from datetime import datetime

def remove_line_breaks(string : str):
    return string.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

def query_res_to_dict(result : Row | list[Row]) -> dict | list[dict]:
    if type(result) == Row:
        return result._asdict()
    else:
        return [row._asdict() for row in result]
    
def get_task_sorting_key(task, sorting : list[str]):
    key = []
    for sort_str in sorting:
        if sort_str == "deadline":
            key.append(task["deadline"] if task["deadline"] else datetime.max)
        elif sort_str == "priority":
            key.append(-task["priority"].value)
        elif sort_str == "state":
            key.append(task["state"].value)
        elif sort_str == "title":
            key.append(task["title"])
        elif sort_str == "project":
            key.append(task["project_title"])
        else:   
            raise ValueError(f"invalid sort string: '{sort_str}'")
    return key
