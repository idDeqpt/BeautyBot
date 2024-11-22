token = ""


def load_token():
    with open("token.txt") as file:
        global token
        token = file.readline()
    return token


if (__name__ == "__main__"):
    print([token])