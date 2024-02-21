# Copyright Exafunction, Inc.

import gzip
import os
import stat
import subprocess
import tempfile
from threading import Thread
import time
from urllib import request

from .xdg_base_dirs import xdg_data_home

import sublime
import sublime_plugin

API_SERVER_URL = "https://server.codeium.com"
LANGUAGE_SERVER_VERSION = "1.6.36"
LANGUAGE_SERVER_PATH = "exa.language_server_pb.LanguageServerService"

import Codeium.requests as requests

codeium_dir = os.path.join(xdg_data_home(), "codeium/sublime")

def plugin_loaded() -> None:
    os.makedirs(codeium_dir, exist_ok=True)
    t = Thread(target=LanguageServerRunner.setup)
    t.start()


def plugin_unloaded() -> None:
    LanguageServerRunner.cleanup()


platform_map = {
    "osx": "macos",
    "windows": "windows",
    "linux": "linux",
}

arch_map = {"x64": "x64", "arm64": "arm"}

ext_map = {
    "osx": ".gz",
    "windows": ".exe.gz",
    "linux": ".gz",
}


class LanguageServerRunner:
    """start the language server"""

    plat = platform_map[sublime.platform()]
    arch = arch_map[sublime.arch()]
    ext = ext_map[sublime.platform()]
    binaryName = "language_server_{plat}_{arch}".format(plat=plat, arch=arch)
    url = "https://github.com/Exafunction/codeium/releases/download/language-server-v{version}/{binaryName}{ext}".format(
        version=LANGUAGE_SERVER_VERSION, binaryName=binaryName, ext=ext
    )
    file = os.path.join(
        codeium_dir, "{binaryName}.download".format(binaryName=binaryName)
    )
    port = -1  # language server port

    @classmethod
    def download_server(cls):
        # download language server
        if not os.path.exists(cls.file):
            with request.urlopen(cls.url) as response:
                with gzip.GzipFile(fileobj=response) as uncompressed:
                    file_content = uncompressed.read()

                    with open(cls.file, "wb") as f:
                        f.write(file_content)

        os.chmod(cls.file, stat.S_IEXEC)

    @classmethod
    def run_server(cls):
        cls.cleanup()
        cls.td = tempfile.TemporaryDirectory()
        manager_dir = cls.td.name
        database_dir = os.path.join(codeium_dir, '..', 'database', 'default')
        args = [
            cls.file,
            "--api_server_url",
            API_SERVER_URL,
            "--manager_dir",
            manager_dir,
            "--database_dir",
            database_dir,
        ]
        with open(os.path.join(codeium_dir, "stdout.txt"), "wb") as out, open(
            os.path.join(codeium_dir, "stderr.txt"), "wb"
        ) as err:
            cls.proc = subprocess.Popen(args, stdout=out, stderr=err)

        start_time = time.time()
        while True:
            files = os.listdir(manager_dir)
            files = [f for f in files if os.path.isfile(os.path.join(manager_dir, f))]
            if len(files) > 0:
                cls.port = int(files[0])
                break

            if time.time() - start_time > 10:
                raise Exception("Language server port file not found after 10 seconds")

            time.sleep(0.1)

    @classmethod
    def make_request(cls, req, respclass):
        if cls.port >= 0:
            resp = requests.post(
                "http://localhost:{port}/{path}/{type}".format(
                    port=cls.port, path=LANGUAGE_SERVER_PATH, type=req.name
                ),
                data=req.buf.SerializeToString(),
                headers={"Content-type": "application/proto"},
            )
            if resp.status_code in range(200, 300):
                obj = respclass()
                obj.ParseFromString(resp.content)
                return obj
            else:
                print(resp.json())
        else:
            raise Exception("Language server did not start")

    @classmethod
    def setup(cls):
        cls.download_server()
        cls.run_server()

    @classmethod
    def cleanup(cls):
        if hasattr(cls, "proc") and cls.proc is not None:
            cls.proc.kill()
            cls.proc = None
