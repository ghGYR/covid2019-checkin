import base64

def encode_json(filename):
    with open(filename,"rt") as f:
        str=f.read().encode("utf-8")
    return base64.b64encode(str)
