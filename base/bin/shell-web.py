import os
import sys

import requests
from bs4 import BeautifulSoup

from N4Tools.Design import Text
from rich.traceback import install

sys.path.extend([
    (base := os.path.abspath(__file__).split('/bin')[0]),
    os.path.join(base, "tools/shell-web"),
])

from shell import BaseShell
from main_shell import MainShell

install()


def data_from_user():
    value = Text().CInput(
        "\x1B[33mUrl-or-File\x1B[32m~\x1B[31m/\x1B[0m$ ",
        completer=list(BaseShell.Path),
        clear_history=False,
    ).strip()
    if os.path.isfile(value):
        with open(value, "r") as f:
            content = f.read()
        return (f, BeautifulSoup(content, "html.parser"), None)
    else:
        try:
            req = requests.get(value)
            content = req.content
        except Exception as e:
            print(f"# {e}")
            return False
        return (req, BeautifulSoup(content, "html.parser"), value)
    print(f"# file {value} not found!")
    return False


while True:
    try:
        if tmp := data_from_user():
            value, html, url = tmp
            break
    except KeyboardInterrupt:
        exit("")

if __name__ == "__main__":
    MainShell(value, html, url).cmdloop()
