from ruamel import yaml

from pyroute2 import IPDB

import subprocess
import sys
import os.path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from proace_gui.Dialog import Dialog

# OTHER WINDOWS
class Settings:

    # SIGNAL HANDLING
    def on_settings_cancel(self, object, data=None):
        self.window.destroy()

    def on_settings_accept(self,object,data=None):
        # Get data
        data = {
            'interface':    self.builder.get_object("gtk_interfaces").get_active_text(),
            'rt_table':     int(self.builder.get_object("gtk_rt_table").get_text()),
            'fwmark':       int(self.builder.get_object("gtk_fwmark").get_text()),
            'group':        self.builder.get_object("gtk_group").get_text()
        }

        # Writing to file with error handling
        #   If the program has permissions to write in the configuration file, run writeToFile.
        #   Otherwise, ask for permissions with self.sudo, and writeToFile
        #   If any other error happens, a dialog box will appear showing the error
        try:
            with open(self.configFilePath, 'w') as configFile: # Load file
                yaml.dump(data, configFile)
            Dialog(self.builder,"Restart required", "Restart the service in order to apply changes")

        except PermissionError:
            # Run proace_sudo/writetofile.py as root to write the data into the file
            if self.pkexec([sys.executable, os.path.abspath("proace_sudo/writetofile.py"), self.configFilePath, yaml.dump(data)]).returncode == 0: # If it was successful
                Dialog(self.builder,"Restart required", "Restart the service in order to apply changes")
            else: # If it wasn't successful
                Dialog(self.builder,"Error", "Error while writing to file")

        except Exception as e:
            Dialog(self.builder,"Error", "Error while writing to file:\n\t"+str(e))


    # FUNCTIONS
    
    # Asks for root permissions and runs command
    #   Returns a CompletedProcess object, containing, among other things, the return code
    def pkexec(self, command):
        return subprocess.run(['pkexec'] + command)

    # Build interfaces dropdown menu
    #   Checks the system interfaces and the configuration file
    #   in order to populate the interfaces drop down menu
    def build_dropdown_interfaces(self):
        # Clear previous dropdown menu items
        gtk_interfaces = self.builder.get_object("gtk_interfaces")
        for _ in range(0, len(self.interfaces)):
            gtk_interfaces.remove(0)

        # Get network interfaces
        with IPDB() as ipdb:
            # For every interface in the system
            for interface in ipdb.by_name.keys():
                # If it's not in the interfaces list, add the interface to the list
                if interface not in self.interfaces:
                    self.interfaces.append(interface)
        
        # Check the interface specified in the config file
        configInterface = self.config.get('interface')
        # Add it to the list if it isn't there
        #   and store the index so it can be set as the active item in the drop down menu
        if configInterface not in self.interfaces:
            self.interfaces.append(configInterface)
            activeItemIndex = len(self.interfaces)-1
        else:
            activeItemIndex = self.interfaces.index(configInterface)

        # Add interfaces to the dropdown menu
        for interface in self.interfaces:
            gtk_interfaces.append_text(interface)

        # Set active item
        gtk_interfaces.set_active(activeItemIndex)

    def build_rt_table(self):
        gtk_rt_table = self.builder.get_object("gtk_rt_table")
        gtk_rt_table.set_text(str(self.config.get('rt_table')))

    def build_fwmark(self):
        gtk_rt_table = self.builder.get_object("gtk_fwmark")
        gtk_rt_table.set_text(str(self.config.get('fwmark')))

    def build_group(self):
        gtk_rt_table = self.builder.get_object("gtk_group")
        gtk_rt_table.set_text(self.config.get('group'))



    # INIT
    def __init__(self, builder, config, configFilePath):
        # Store builder and config on the object itself
        self.builder = builder
        self.config = config
        self.configFilePath = configFilePath

        # Load interface from file
        self.builder.add_from_file("glade/settings.glade") # add the xml file to the Builder
        self.builder.connect_signals(self) # Connect signals

        # Build dialog window
        self.window = builder.get_object("settings1") # This gets the 'settings1' object
        self.window.show() # this shows the 'settings1' object

        # Populate settings menu
            # Interfaces
        self.interfaces = []
        self.build_dropdown_interfaces()
            # rt_table
        self.build_rt_table()
            # fwmark
        self.build_fwmark()
            # group
        self.build_group()