import json
import os
import re

import requests
from N4Tools.Design import ThreadAnimation
from bs4 import BeautifulSoup
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer

from html_shell import HtmlShell
from source import Source
from shell import BaseShell


class MainShell(BaseShell):  # Main Shell
    ToolName = "Shell-Web"

    def __init__(self, value, html, url, *args, **kwargs):
        super(MainShell, self).__init__(*args, *kwargs)
        self.value = value
        self.html = html
        self.url = url
        self.Names = {"rest": []}  # Mode: [ Urls ]
        for x in re.findall('"((http|ftp)s?://.*?)"', html.prettify()):
            x = x[0]
            if x.endswith('/'):
                self.Names["rest"].append(x)
            else:
                line = x.split('/')[-1]
                if '.' in line:
                    line = line.split('.')[-1]
                    if [c for c in re.findall('[\W]*', line) if c] or '_' in line:
                        self.Names["rest"].append(x)
                    else:
                        if line in self.Names:
                            self.Names[line].append(x)
                        else:
                            self.Names[line] = [x]
                else:
                    self.Names["rest"].append(x)
        self.Names = {
            a: list(set(self.Names[a]))
            for a in sorted(list(self.Names.keys()))
        }

    def do_html(self, arg):
        HtmlShell(self.html).cmdloop()

    def do_Flask(self, arg):
        if not arg.startswith('<') and not arg.endswith('/>'):
            if os.path.exists(arg.strip()):
                os.system(f'python3 -B {arg}')
            else:
                 print(f"# not filename: '{arg}'")
            return
        soup = BeautifulSoup(arg, "html.parser")
        soup = soup.find("flask")
        if all(data := [soup.get('appname'), soup.get('pagename')]):
            if url := soup.get('url'):
                try:
                    content = requests.get(url).content
                except Exception as e:
                    print(f"# {e}")
                    return
                Source(*data, url, BeautifulSoup(content, "html.parser").prettify()).start()
            elif url := self.url:
                Source(*data, url, self.html.prettify()).start()
            else:
                print(f"USAGE:\n  Flask <flask appname='webname' pagename='index' url='https://example.com'/>")
        else:
            print(f"USAGE:\n  Flask <flask appname='webname' pagename='index'/>")

    def complete_Flask(self, *args):
        url = "" if self.url else "url=''"
        return [f"<flask appname='' pagename='index' {url}/>"]

    @ThreadAnimation()
    def Lexer_Json(self, Thread, Code):
        out = highlight(Code, JsonLexer(), TerminalFormatter())
        Thread.kill = True
        return out

    def do_Info(self, arg):
        if type(self.value) == str:
            print("# you are using file!")
        elif len((f := [x for x in re.findall("[\W]*", arg.strip()) if x])) > 0:
            print("# you are using file!")
        else:
            try:
                temp = eval(f'self.value.{arg}')
            except Exception as e:
                print("\033[1;31mERROR:\033[0m", e)
            else:
                if type(temp) == dict or arg == "headers":
                    print(
                        self.Lexer_Json(
                            str(
                                json.dumps(
                                    dict(temp),
                                    indent=3
                                )
                            )
                        )
                    )
                else:
                    print(temp)

    def complete_Info(self, line, *args):
        if type(self.value) == str:
            return ["None"]
        Del = ["text", "_content", "iter_content", "iter_lines", "json"]
        all = [
            x for x in dir(self.value)
            if not x.startswith('__') and x not in Del
        ]
        return [x for x in all if x.startswith(line)] if line else all

    def do_Link(self, arg):  # Links-Urls
        if arg:
            for x in (self.Names[arg]):
                print(f'\033[1;31m-> \033[1;37m{x}\033[0m')

    def complete_Link(self, line, *args):
        all = list(self.Names.keys()) + ["rest"]
        return [x for x in all if x.startswith(line)] if line else all
