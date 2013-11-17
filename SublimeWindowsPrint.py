import sublime
import sublime_plugin
import os
import subprocess


def load_settings():
    return sublime.load_settings("SublimeWindowsPrint.sublime-settings")

def save_settings():
    sublime.save_settings("SublimeWindowsPrint.sublime-settings")

def open_pipe(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)


class SublimeWindowsPrint(sublime_plugin.WindowCommand):
    '''
    Base class for the print commands. Handles creating the printer list and
    setting options to the printer command.
    '''

    def is_enabled(self):
        '''
        Print commands normally requires an active view.
        '''
        return self.window.active_view() != None

    def find_command(self, cmd):
        '''
        If the given command exists, return it, otherwise return none.
        '''
        if not os.path.isfile(cmd):
            sublime.error_message("Command '" + cmd + "' not found! Check the command in the settings file.")
            cmd = None

        return cmd

    def printer_command(self):
        '''
        Return the array of command line options to pass to the subprocess.
        '''
        settings = load_settings()
        print_cmd = self.find_command(settings.get("print_command_path"))
        if print_cmd is None: return None

        return print_cmd

    def send_file_to_printer(self, cmd, file_path):
        cmd + " " + file_path
        p = open_pipe(cmd)
        ret = p.wait()

        if ret:
            raise EnvironmentError((cmd, ret, p.stdout.read()))


class PrintFileCommand(SublimeWindowsPrint):
    '''
    Print the current file.
    '''
    def run(self):
        file_path = self.window.active_view().file_name()
        if self.window.active_view().is_dirty():
            sublime.message_dialog("File has unsaved changes.")
            return
        elif not file_path:
            sublime.message_dialog("No file to print.")
            return

        cmd = self.printer_command()
        if cmd is not None:
            self.send_file_to_printer(cmd, file_path)