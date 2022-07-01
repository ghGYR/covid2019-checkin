import base64

def encode_json(filename):
    with open(filename,"rb") as f:
        str=f.read()
    return base64.b64encode(str)
