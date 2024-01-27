# Copyright Exafunction, Inc.

import os
import random
import string
import webbrowser

import Codeium.requests as requests
import sublime
import sublime_plugin

codeium_dir = os.path.join(os.path.expanduser("~"), ".codeium/sublime")

API_KEY_FILE = os.path.join(codeium_dir, "codeium-api-key.txt")


class CodeiumSettings:
    enable = True
    api_key = ""
    session_id = random.randrange(0, 1000000)
    request_id = 1


if os.path.exists(API_KEY_FILE):
    with open(API_KEY_FILE, "r") as f:
        CodeiumSettings.api_key = f.read()

SIGN_IN_URL = "https://www.codeium.com/profile?response_type=token&redirect_uri=show-auth-token&state=a&scope=openid%20profile%20email&redirect_parameters_type=query"
REGISTER_USER_URL = "https://api.codeium.com/register_user/"


class CodeiumEnablePluginCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CodeiumSettings.enable = True
        print("enable")


class CodeiumDisablePluginCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        CodeiumSettings.enable = False
        self.view.settings().set("Codeium.completion_active", False)
        print("disable")


class CodeiumSignInCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        webbrowser.open(SIGN_IN_URL)


class CodeiumProvideAuthTokenCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        def on_done(auth_token):
            r = requests.post(
                REGISTER_USER_URL, json={"firebase_id_token": auth_token}, verify=False
            )
            if r.status_code == 200:
                CodeiumSettings.api_key = r.json()["api_key"]
                with open(API_KEY_FILE, "w") as f:
                    f.write(CodeiumSettings.api_key)
                print("Sign In Succeeded")
                window = self.view.window()
                panel = window.create_output_panel("out")
                panel.run_command(
                    "insert",
                    {
                        "characters": "Success! Please restart sublime to start using the plugin"
                    },
                )
                window.run_command("show_panel", {"panel": "output.out"})
            else:
                print("Sign In Failed")

        window = self.view.window()
        window.show_input_panel(
            "Press 'Enter' to confirm your input':", "", on_done, None, None
        )
