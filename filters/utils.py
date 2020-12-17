def strip_slug(s):
    parts = s.split("/")
    return parts[-1]

def dataset_name(s):
    s = s.replace("-", " ")
    return s.capitalize()