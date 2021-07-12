import re

from N4Tools.Design import ThreadAnimation
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.html import HtmlLexer

from shell import BaseShell


class HtmlShell(BaseShell):
    ToolName = "Shell-Web.Html"

    def __init__(self, html, *args, **kwargs):
        super(HtmlShell, self).__init__(*args, **kwargs)
        self.html = html

    def completenames(self, text, *args):
        base_command = ["back", "clear", "exit"] if text else []
        out = [
                   tag for tag in self.html.open_tag_counter.keys()
                   if tag.startswith(text)
               ] + [_ for _ in base_command if _.startswith(text)]
        return [f"<{out[0]}/>"] if len(out) == 1 else out

    def completedefault(self, text, line, *args):
        return []

    def default(self, line):
        pattern = r'''\<((\w+)((?:\.\w+)|(?:\[["']\w+["']\]))?)((?: \w+=["'][\w\*\+/\- ]+["'])+)?\/\>'''
        find_tags = re.findall(pattern, line)
        if not find_tags:
            print("EXAMPLES:")
            print(" <div/>")
            print(' <div class="style2"/>')
            print(' <div class="style2" width="200"/>')
            print(' <h5.text class="style2"/>')
            print(' <a["href"]/>')
            print(' <img["src"]/>')
            print(' <img["src"]/> <a/>')
        try:
            for data in find_tags:
                _tag_name = data[1]
                _attr = data[2]
                _options = re.findall(r'''(\w+=["'][\w\*\+/\- ]+["'])+''', data[3])

                soup = self.html.findAll(_tag_name)
                if _options:
                    _tmp = {}
                    for option in _options:
                        _tmp[option.split("=")[0].replace("class", "class_")] = option.split("=")[1][1:-1]
                    soup = self.html.findAll(_tag_name, **_tmp)

                for tag in soup:
                    if _attr:
                        try:
                            print(str(eval(f"tag{_attr}")))
                        except KeyError:
                            pass
                    else:
                        self.lexer_html(tag.prettify())
        except KeyboardInterrupt:
            print("")

    @ThreadAnimation()
    def lexer_html(Thread, self, Code):
        out = highlight(Code, HtmlLexer(), TerminalFormatter())
        Thread.set_end(out)

    def do_back(self, arg):
        return True
