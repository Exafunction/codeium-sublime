# Copyright Exafunction, Inc.

import html
import logging
from threading import Lock
from threading import Thread

from Codeium.login import CodeiumSettings
from Codeium.protorequests import CancelRequestRequest
from Codeium.protorequests import GetCompletionsRequest
import sublime
import sublime_plugin

CODEIUM_STATE_SUCCESS = 3

COMPLETION_PART_TYPE_UNSPECIFIED = 0
COMPLETION_PART_TYPE_INLINE = 1
COMPLETION_PART_TYPE_BLOCK = 2
COMPLETION_PART_TYPE_INLINE_MASK = 3


class CodeiumCompletionPart:
    def __init__(self, text, point):
        self.text = text
        self.point = point


class CodeiumCompletion:
    def __init__(self):
        self.inline_parts = []
        self.block = None

    def add_inline(self, text, point):
        self.inline_parts.append(CodeiumCompletionPart(text, point))

    def add_block(self, text, point):
        self.block = CodeiumCompletionPart(text, point)


def is_active_view(obj):
    return bool(obj and obj == sublime.active_window().active_view())


lock = Lock()

completions = []
index = 0
display = False
for_position = -1


def make_async_request(req, view):
    global completions, index, for_position
    print("sent completion request")
    resp = req.send()
    if resp and resp.state.state == CODEIUM_STATE_SUCCESS:
        print("response is:", resp.state.message)
        c = []
        for item in resp.completion_items:
            completion = CodeiumCompletion()
            for part in item.completion_parts:
                offset = view.text_point_utf8(0, part.offset)
                if part.type == COMPLETION_PART_TYPE_INLINE:
                    completion.add_inline(part.text, offset)
                elif part.type == COMPLETION_PART_TYPE_BLOCK:
                    completion.add_block(part.text, offset)
            c.append(completion)
        if len(c) > 0:
            lock.acquire()
            completions = c
            index = -1
            for_position = view.sel()[0].begin()
            lock.release()
            view.settings().set("Codeium.completion_active", True)
            view.run_command("codeium_display_completion")


class RequestCompletionListener(sublime_plugin.EventListener):
    def on_modified_async(self, view):
        if (
            is_active_view(view)
            and CodeiumSettings.enable
            and CodeiumSettings.api_key != ""
        ):
            if hasattr(self, "req") and hasattr(getattr(self, "req"), "id"):
                # cancel previous request
                print("sent cancel")
                CancelRequestRequest(getattr(self, "req").id).send()
            self.req = GetCompletionsRequest(view)
            ## start the thread
            t = Thread(target=make_async_request, args=[self.req, view])
            t.start()

    def on_selection_modified_async(self, view):
        global for_position
        if (
            is_active_view(view)
            and for_position != -1
            and view.sel()[0].begin() != for_position
        ):
            PhantomCompletion.hide(view)
            for_position = -1


class CodeiumDisplayCompletionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global completions, index, display
        if for_position != -1:
            lock.acquire()
            index = (index + 1) % len(completions)
            lock.release()
            PhantomCompletion(self.view, completions[index]).show(edit)


class CodeiumDisplayPreviousCompletionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global completions, index, display
        if for_position != -1:
            lock.acquire()
            index = (index + len(completions) - 1) % len(completions)
            lock.release()
            PhantomCompletion(self.view, completions[index]).show(edit)


class CodeiumRejectCompletionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global completions, index, display
        PhantomCompletion.hide(self.view)
        lock.acquire()
        for_position = -1
        lock.release()
        self.view.settings().set("Codeium.completion_active", False)


class CodeiumAcceptCompletionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global for_position
        if for_position != -1:
            PhantomCompletion.hide(self.view)
            PhantomCompletion(self.view, completions[index]).make_real(edit)
            lock.acquire()
            for_position = -1
            lock.release()
        self.view.settings().set("Codeium.completion_active", False)


_view_to_phantom_set = {}


class PhantomCompletion:
    PHANTOM_TEMPLATE = """
    <body id="codeium-completion">
        <style>
            body {{
                color: #808080;
                font-style: italic;
            }}

            .codeium-completion-line {{
                line-height: 0;
                margin-top: {line_padding_top}px;
                margin-bottom: {line_padding_bottom}px;
                margin-left : 0;
                margin-right : 0;
            }}

            .codeium-completion-line.first {{
                margin-top: 0;
            }}
        </style>
        {body}
    </body>
    """
    PHANTOM_LINE_TEMPLATE = '<div class="codeium-completion-line">{content}</div>'

    def __init__(
        self,
        view: sublime.View,
        completion,
    ) -> None:
        self.view = view
        self._settings = view.settings()
        self._phantom_set = self._get_phantom_set(view)
        self.completion = completion

    @classmethod
    def _get_phantom_set(cls, view: sublime.View) -> sublime.PhantomSet:
        view_id = view.id()

        # create phantom set if there is no existing one
        if not _view_to_phantom_set.get(view_id):
            _view_to_phantom_set[view_id] = sublime.PhantomSet(view)

        return _view_to_phantom_set[view_id]

    def normalize_phantom_line(self, line: str) -> str:
        return (
            html.escape(line)
            .replace(" ", "&nbsp;")
            .replace("\t", "&nbsp;" * self._settings.get("tab_size"))
        )

    def _build_phantom(
        self,
        lines,
        begin: int,
        end=None,
        *,
        inline: bool = True
        # format separator
    ) -> sublime.Phantom:
        body = (
            self.normalize_phantom_line(lines)
            if isinstance(lines, str)
            else "".join(
                self.PHANTOM_LINE_TEMPLATE.format(
                    class_name=("rest" if index else "first"),
                    content=self.normalize_phantom_line(line),
                )
                for index, line in enumerate(lines)
            )
        )

        return sublime.Phantom(
            sublime.Region(begin, begin if end is None else end),
            self.PHANTOM_TEMPLATE.format(
                body=body,
                line_padding_top=int(self._settings.get("line_padding_top"))
                * 2,  # TODO: play with this more
                line_padding_bottom=int(self._settings.get("line_padding_bottom")) * 2,
            ),
            sublime.LAYOUT_INLINE if inline else sublime.LAYOUT_BLOCK,
        )

    def _add_text(self, edit, text, point):
        # region = sublime.Region(begin, begin if end is None else end)
        self.view.insert(edit, point, text)
        # return region.end()

    def show(self, edit) -> None:
        # first_line, *rest_lines = self.completion.text.splitlines()
        assert self._phantom_set
        self._phantom_set.update([])

        cursor = self.view.sel()[0].begin()
        completion = self.completion
        phantom_set = []

        for part in completion.inline_parts:
            phantom_set.append(
                self._build_phantom(part.text, part.point, self.view.size())
            )

        if completion.block:
            phantom_set.append(
                self._build_phantom(
                    completion.block.text.splitlines(),
                    completion.block.point,
                    inline=False,
                )
            )
        else:
            phantom_set.append(
                self._build_phantom("", self.view.line(cursor).end(), inline=False)
            )

        self._phantom_set.update(phantom_set)

    def make_real(self, edit):
        line_ending = "\r\n" if "Windows" in self.view.line_endings() else "\n"
        completion = self.completion
        cursor = self.view.sel()[0].begin()
        added = []
        for part in completion.inline_parts:
            shift = 0
            for pos, amt in added:
                if pos < part.point:
                    shift += amt
            self._add_text(edit, part.text, part.point + shift)
            added.append((part.point, len(part.text)))
        # move cursor to the end of the line
        self.view.sel().clear()
        line = self.view.line(cursor)
        self.view.sel().add(line.end())

        if completion.block:
            text = line_ending + completion.block.text
            self._add_text(edit, text, self.view.line(completion.block.point).end())

    @classmethod
    def hide(cls, view: sublime.View) -> None:
        cls._get_phantom_set(view).update([])

    @classmethod
    def close(cls, view: sublime.View) -> None:
        del _view_to_phantom_set[view.id()]
