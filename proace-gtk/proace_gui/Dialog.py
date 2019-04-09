# OTHER WINDOWS
class Dialog:

    # SIGNAL HANDLING
    def on_dialog1_destroy(self, obj):
        # Run accept_callback if it was specified
        if self.accept_callback != None:
            self.accept_callback()
        # Otherwise, just close the window
        else:
            self.window.destroy()

    def on_dialog_accept(self, object, data=None):
        # Run accept_callback if it was specified
        if self.accept_callback != None:
            self.accept_callback()
        # Otherwise, just close the window
        else:
            self.window.destroy()

    # INIT
    def __init__(self, builder, title, label, accept_callback=None):
        # Store accept_callback and builder on the object itself
        self.builder = builder
        self.accept_callback = accept_callback

        # Load interface from file
        self.builder.add_from_file("glade/dialog.glade") # add the xml file to the Builder
        self.builder.connect_signals(self) # Connect signals

        # Build dialog window
        self.window = builder.get_object("dialog1") # This gets the 'dialog1' object
        self.window.show() # this shows the 'dialog1' object

        # Set title and label text
        self.window.set_title(title)
        builder.get_object("gtk_dialog_label").set_label(label)