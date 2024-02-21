# Copyright Exafunction, Inc.

from abc import ABC
from abc import abstractmethod
import os
import random
import sys

from Codeium.exa.codeium_common_pb import codeium_common_pb2
from Codeium.exa.language_server_pb import language_server_pb2
from Codeium.language_server import LANGUAGE_SERVER_VERSION
from Codeium.language_server import LanguageServerRunner
from Codeium.login import CodeiumSettings
import Codeium.requests as requests
import sublime
import sublime_plugin

enum = codeium_common_pb2.Language

lang_map = {
    "Python": enum.LANGUAGE_PYTHON,
    "Java": enum.LANGUAGE_JAVA,
    "C++": enum.LANGUAGE_CPP,
}


### HELPERS FOR THE REQUEST OBJECTS


class Request(ABC):
    @abstractmethod
    def send(self):
        pass


def populate_metadata(metadata):
    metadata.ide_name = "sublime_text"
    metadata.ide_version = sublime.version()
    metadata.extension_version = LANGUAGE_SERVER_VERSION
    metadata.api_key = CodeiumSettings.api_key
    metadata.session_id = str(CodeiumSettings.session_id)
    metadata.request_id = CodeiumSettings.request_id
    CodeiumSettings.request_id += 1


### REQUEST OBJECTS


class GetCompletionsRequest(Request):
    name = "GetCompletions"

    def __init__(self, view):
        self.view = view
        # construct request
        buf = language_server_pb2.GetCompletionsRequest()
        self.make_document(buf.document)
        self.make_metadata(buf.metadata)
        self.make_editor_options(buf.editor_options)
        self.buf = buf

    def send(self):
        # send request
        resp = LanguageServerRunner.make_request(
            self, language_server_pb2.GetCompletionsResponse
        )
        return resp

    def make_document(self, doc):
        view = self.view
        sel = view.sel()
        if len(sel) != 1:
            raise Exception("have more than one cursor")

        beg = sublime.Region(0, sel[0].begin())
        end = sel[0]

        cursor_offset = len(view.substr(beg).encode(encoding="utf-8"))
        settings = view.settings()
        doc.absolute_path = " " if view.file_name() is None else view.file_name()
        doc.relative_path = os.path.relpath(doc.absolute_path)
        doc.text = view.substr(sublime.Region(0, view.size()))
        doc.editor_language = settings.get("syntax").split("/")[1]
        doc.language = (
            lang_map[doc.editor_language]
            if doc.editor_language in lang_map
            else enum.LANGUAGE_UNSPECIFIED
        )
        doc.cursor_offset = cursor_offset
        doc.line_ending = "\r\n" if "Windows" in view.line_endings() else "\n"

    def make_metadata(self, metadata):
        populate_metadata(metadata)
        self.id = metadata.request_id

    def make_editor_options(self, options):
        view = self.view
        options.tab_size = view.settings().get("tab_size")
        options.insert_spaces = view.settings().get("translate_tabs_to_spaces")


class CancelRequestRequest(Request):
    name = "CancelRequest"

    def __init__(self, id):
        self.id = id

    def send(self):
        buf = language_server_pb2.CancelRequestRequest()
        try:
            populate_metadata(buf.metadata)
        except:
            return
        buf.request_id = self.id
        self.buf = buf
        resp = LanguageServerRunner.make_request(
            self, language_server_pb2.CancelRequestResponse
        )
        return resp
