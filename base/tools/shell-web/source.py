import os
import re

import requests
from N4Tools.Design import ThreadAnimation
from bs4 import BeautifulSoup


class Source:
    def __init__(self, appname, pagename, url, html_page_text):
        self.appname = appname
        self.pagename = pagename
        self.url = url
        self.html_soup = BeautifulSoup(html_page_text, "html.parser")
        self.domin = '//'.join([x for x in url.split('/') if x][:2])
        self.paths = [
            f"{appname}",
            f"{appname}/static",
            f"{appname}/templates",
        ]
        self.main_app = os.path.join(appname, '__main__.py')
        if os.path.exists(self.main_app):
            with open(os.path.join(appname, "__main__.py"), 'r') as file:
                self.app_text_file = file.read()
        else:
            with open(os.path.abspath(__file__).rsplit("/", 1)[0] + "/flask_app.py", 'r') as file:
                self.app_text_file = file.read()

    @ThreadAnimation()
    def install_static_files(Thread, self, url):
        filename = os.path.join(self.appname, f'static/{url.split("/")[-1]}')
        if os.path.exists(filename):
            return '{{ url_for("static", filename="%s") }}' % url.split("/")[-1]
        try:
            content = requests.get(url).content
            with open(filename, 'wb') as file:
                file.write(content)
            Thread.set_end(
                f"[\033[0;33mstate\033[0m \033[0;32mtrue\033[0m] {filename}"
            )
            return '{{ url_for("static", filename="%s") }}' % url.split("/")[-1]
        except Exception as e:
            Thread.set_end(
                f"[\033[0;33mstate\033[0m \033[0;31mfalse\033[0m] {filename}"
            )
            return None

    def download_app_files(self):
        pattren_http = r'https?:.*\.(?:jpg|png|jpeg|gif|svg|css|js|ico)'
        pattren_domain = r'^\/.+\.(?:jpg|png|jpeg|gif|svg|css|js|ico)'
        for tag in self.html_soup.open_tag_counter.keys():
            for soup in self.html_soup.find_all(tag):
                for attr in ['src', 'href', 'content']:
                    if text := soup.get(attr):
                        if url := re.search(pattren_http, text):
                            if file := self.install_static_files(url[0]):
                                soup[attr] = file
                        elif url := re.search(pattren_domain, text):
                            url.start()
                            if file := self.install_static_files(self.domin + url[0]):
                                soup[attr] = file

    def create_app_folders(self):
        for folder in self.paths:
            try:
                os.mkdir(folder)
            except FileExistsError:
                pass

    def page(self, page_name):
        return f'''\n\n@app.route('{page_name}')\ndef {page_name[1:]}():\n    # Code...\n    return render_template('{page_name[1:]}.html')'''

    def start(self):
        self.create_app_folders()
        self.download_app_files()
        pattern = r'''(\@\w+\.route\(["'](.+)["']\)\s+def \w+\(.*\):\s(?:[ \t]+.+\n){1,}\s+return render_template\(['"](.+)['"]\))'''
        page_functions = re.findall(pattern, self.app_text_file)
        pages = []
        for function in page_functions:
            function_body, page_route, page_file = function
            pages.append(page_route)
        if (page_name := '/' + self.pagename.replace('index', '')) not in pages:
            new_page = function_body + self.page(page_name)
            self.app_text_file = self.app_text_file.replace(
                function_body, new_page
            )
            pages.append(page_name)

        with open(os.path.join(self.appname, "templates", f"{self.pagename}.html"), "w") as file:
            file.write(self.html_soup.prettify())
        with open(self.main_app, 'w') as file:
            file.write(self.app_text_file)

        print(f"\033[0;33mPAGES:", *pages, sep='\n  \033[0m')
        print(f"\n# DONE ✅")
