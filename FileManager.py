# -*- encoding: utf-8 -*-
import sys
import sublime
import sublime_plugin

# Clear module cache to force reloading all modules of this package.
prefix = __package__ + "."  # don't clear the base package
for module_name in [
    module_name
    for module_name in sys.modules
    if module_name.startswith(prefix) and module_name != __name__
]:
    del sys.modules[module_name]
prefix = None

from .commands.copy import FmCopyCommand
from .commands.create import FmCreaterCommand, FmCreateCommand
from .commands.create_from_selection import FmCreateFileFromSelectionCommand
from .commands.delete import FmDeleteCommand
from .commands.duplicate import FmDuplicateCommand
from .commands.editto import FmEditToTheLeftCommand, FmEditToTheRightCommand
from .commands.find_in_files import FmFindInFilesCommand
from .commands.move import FmMoveCommand
from .commands.open_all import FmOpenAllCommand
from .commands.open_in_browser import FmOpenInBrowserCommand
from .commands.open_in_explorer import FmOpenInExplorerCommand
from .commands.open_terminal import FmOpenTerminalCommand
from .commands.rename import FmRenameCommand, FmRenamePathCommand


def plugin_loaded():
    settings = sublime.load_settings("FileManager.sublime-settings")


class FmEditReplace(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        kwargs.get("view", self.view).replace(
            edit, sublime.Region(*kwargs["region"]), kwargs["text"]
        )


class FmListener(sublime_plugin.EventListener):
    def on_load(self, view):
        settings = view.settings()
        snippet = settings.get("fm_insert_snippet_on_load", None)
        if snippet:
            view.run_command("insert_snippet", {"contents": snippet})
            settings.erase("fm_insert_snippet_on_load")
            if sublime.load_settings("FileManager.sublime-settings").get(
                "save_after_creating"
            ):
                view.run_command("save")
            if settings.get("fm_reveal_in_sidebar"):
                view.window().run_command("reveal_in_side_bar")

    def on_text_command(self, view, command, args):
        if (
            command not in ["undo", "unindent"]
            or view.name() != "FileManager::input-for-path"
        ):
            return
        settings = view.settings()
        if command == "unindent":
            index = settings.get("completions_index")
            settings.set("go_backwards", True)
            view.run_command("insert", {"characters": "\t"})
            return
        # command_history: (command, args, times)
        first = view.command_history(0)
        if first[0] != "fm_edit_replace" or first[2] != 1:
            return
        second = view.command_history(-1)
        if (second[0] != "reindent") and not (
            second[0] == "insert" and second[1] == {"characters": "\t"}
        ):
            return
        settings.set("ran_undo", True)
        view.run_command("undo")
        index = settings.get("completions_index")
        if index == 0 or index is None:
            settings.erase("completions")
            settings.erase("completions_index")
        else:
            settings.set("completions_index", index - 1)
