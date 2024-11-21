def remove_line_breaks(string : str):
    return string.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
