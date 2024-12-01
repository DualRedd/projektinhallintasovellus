from sqlalchemy import Row

def remove_line_breaks(string : str):
    return string.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')

def query_res_to_dict(result : Row | list[Row]) -> dict | list[dict]:
    if type(result) == Row:
        return result._asdict()
    else:
        return [row._asdict() for row in result]
