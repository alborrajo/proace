from ruamel import yaml

import subprocess

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from proace_gui.Dialog import Dialog
from proace_gui.Settings import Settings

class Proace:

    # SIGNAL HANDLING

    # Closing the window
    def on_window1_destroy(self, obj):
        Gtk.main_quit()

    # -- Menu bar

    # Starting the service
    #   This action requires root privileges
    def on_service_start(self, object, data=None):
        # Run proace_sudo/start.py as root to setup the rules and routes
        if self.gksudo(["./proace_sudo/start.sh", self.config.get("interface"), str(self.config.get("rt_table")), str(self.config.get("fwmark")), self.config.get("group")], "Set up rules and routes").returncode == 0: # If it was successful
            self.reload_config() # Reload config to keep up with any changes
        else: # If it wasn't successful
            Dialog(self.builder,"Error", "Error while setting up rules and routes")

    # Stopping the service
    #   This action requires root privileges
    def on_service_stop(self, object, data=None):
        # Run proace_sudo/stop.py as root to undo the setup
        if self.gksudo(["./proace_sudo/stop.sh", self.config.get("interface"), str(self.config.get("rt_table")), str(self.config.get("fwmark")), self.config.get("group")], "Undo rules and routes").returncode == 0: # If it was successful
            self.reload_config() # Reload config to keep up with any changes
        else: # If it wasn't successful
            Dialog(self.builder,"Error", "Error while removing rules and routes")

    # Settings menu
    def on_settings_button(self, object, data=None):
        self.reload_config() # Reload config data before launching settings menu
        Settings(self.builder, self.config, self.configFilePath)

    # -- App Chooser
    #   Selecting an app
    def on_application_activated(self, object, data=None):
        appToRun = data.get_executable()
        print(appToRun)
        self.run(appToRun)

    # -- File Chooser
    #   Clicking the run/execute button
    def on_run_file(self, object, data=None):
        fileToRun = self.builder.get_object("gtk_file_chooser").get_filename()
        print(fileToRun)
        self.run(fileToRun)


    # FUNCTIONS

    # Reload configuration file
    def reload_config(self):
        self.config = yaml.safe_load(open(self.configFilePath,"r").read())         

    # Asks for root permissions and runs command
    #   Returns a CompletedProcess object, containing, among other things, the return code
    def gksudo(self, command, description=None):
        if description == None:
            return subprocess.run(['gksudo'] + command)
        else:
            return subprocess.run(['gksudo', '-D', description] + command)


    # Run applications through the proace group
    #   is the sgame as running "sg proace 'command'"
    def run(self, command):
        # Reload config before running the command to keep up with any changes
        self.reload_config()
        # Run application with "sg", using the group set in the config file
        return subprocess.Popen(['sg', self.config.get('group'), command])


    # INIT
    def __init__(self, builder, config, configFilePath):
        # Store parameters in the object
        self.builder = builder
        self.config = config
        self.configFilePath = configFilePath

        # Load interface from file
        self.builder.add_from_file("glade/proace.glade")

        # Connect signals
        self.builder.connect_signals(self)

        # Build interface
        self.builder.get_object("window1").show() # Show "window1" object