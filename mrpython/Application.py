from MainView import MainView
from tkinter import Tk, sys
from PyEditor import PyEditor
import Bindings

class Application:
    """
    The main class of the application
    - root is the starting point of the GUI application
    - main_view defines the main window
    - py_editor_list defines the editor interface (from the main_view)
    - py_shell defines the shell interface (white and orange widgets)
    """

    def __init__(self):
        """ Set up some information like, set up the interfaces """
        self.root = Tk()
        self.root.title("MrPython")        
        self.mode = "full"
        self.main_view = MainView(self)
        self.editor_list = self.main_view.editor_widget.py_notebook
        self.icon_widget = self.main_view.icon_widget
        self.status_bar = self.main_view.status_bar
        self.console = self.main_view.console
        self.change_mode()
        self.apply_bindings()
        self.root.protocol('WM_DELETE_WINDOW', self.close_all_event)


    def run(self):
        """ Run the application """
        self.main_view.show()


    def apply_bindings(self, keydefs=None):
        """ Bind the actions to the related event methods """
        self.new_file_button = self.icon_widget.icon_new_file_label
        self.run_button = self.icon_widget.icon_run_label
        self.save_button = self.icon_widget.icon_save_label
        self.open_button = self.icon_widget.icon_open_label
        self.mode_button = self.icon_widget.icon_mode_label
        self.new_file_button.bind("<1>", self.new_file)
        self.run_button.bind("<1>", self.run_module)
        self.mode_button.bind("<1>", self.change_mode)
        self.save_button.bind("<1>", self.save)
        self.open_button.bind("<1>", self.open)
        # File
        self.root.bind("<Control-n>", self.new_file)
        self.root.bind('<<open-window-from-file>>', self.open)
        self.root.bind('<<save-window>>', self.save)
        self.root.bind('<<save-window-as-file>>', self.editor_list.save_as)
        self.root.bind('<<save-copy-of-window-as-file>>',
                       self.editor_list.save_as_copy)
        self.root.bind('<<close-window>>',
                       self.editor_list.close_current_editor)
        self.root.bind('<<close-all-windows>>', self.close_all_event)
        # Edit
        self.root.bind('<<undo>>', self.editor_list.undo_event)
        self.root.bind('<<redo>>', self.editor_list.redo_event)
        self.root.bind('<<cut>>', self.editor_list.cut_event)
        self.root.bind('<<copy>>', self.editor_list.copy_event)
        self.root.bind('<<paste>>', self.editor_list.paste_event)
        self.root.bind('<<select-all>>', self.editor_list.select_all_event)
        self.root.bind('<<find>>', self.editor_list.find_event)
        self.root.bind('<<find-again>>', self.editor_list.find_again_event)
        self.root.bind('<<find-selection>>',
                       self.editor_list.find_selection_event)
        self.root.bind('<<find-in-files>>',
                       self.editor_list.find_in_files_event)
        self.root.bind('<<replace>>', self.editor_list.replace_event)
        self.root.bind('<<goto-line>>', self.editor_list.goto_line_event)
        # Format
        self.root.bind('<Control-i>', self.editor_list.indent_region_event)
        self.root.bind('<Control-d>', self.editor_list.dedent_region_event)
        self.root.bind('<<comment-region>>', self.editor_list.comment_region_event)
        self.root.bind('<<uncomment-region>>', self.editor_list.uncomment_region_event)
        self.root.bind('<<tabify-region>>', self.editor_list.tabify_region_event)
        self.root.bind('<<untabify-region>>', self.editor_list.untabify_region_event)
        self.root.bind('<<toggle-tabs>>', self.editor_list.toggle_tabs_event)
        # Code execution
        self.root.bind('<<check-module>>', self.check_module)
        self.root.bind('<Control-r>', self.run_module)
        self.root.bind('<Control-Key-Return>', self.run_source)
        # File change in notebook
        self.root.bind('<<NotebookTabChanged>>', self.update_title)
        # Bind the keys
        if keydefs is None:
            keydefs = Bindings.default_keydefs
        for event, keylist in keydefs.items():
            if keylist:
                self.root.event_add(event, *keylist)


    def update_title(self, event=None):
        """ Give the title the current filename """
        new_title = self.editor_list.tab(self.editor_list.index("current"), "text")
        directory = ""
        if self.editor_list.get_current_editor().io.filename:
            directory = self.editor_list.get_current_editor().io.filename
        if directory != "":
            new_title += " (" + directory + ")"
        new_title += " - MrPython"
        self.root.title(new_title)


    def save(self, event=None):
        """ Save the current file (and display it in the status bar) """
        filename = self.editor_list.save()
        if filename:
            self.status_bar.update_save_label(filename)
            self.update_title()


    def change_mode(self, event=None):
        """ Swap the python mode : full python or student """
        if self.mode == "student":
            self.mode = "full"
        else:
            self.mode = "student"
        self.icon_widget.switch_icon_mode(self.mode)
        self.console.change_mode(self.mode)
        self.status_bar.change_mode(self.mode)


    def new_file(self, event=None):
        """ Creates a new empty editor and put it into the pyEditorList """
        file_editor = PyEditor(self.editor_list)        
        self.editor_list.add(file_editor, text=file_editor.get_file_name())
		

    def open(self, event=None):
        """ Open a file in the text editor """
        file_editor = PyEditor(self.editor_list, open=True)
        if (self.editor_list.focusOn(file_editor.long_title()) == False):
            if (file_editor.isOpen()):
                self.editor_list.add(file_editor, text=file_editor.get_file_name())


    def close_all_event(self, event=None):
        """ Quit all the PyEditor : called when exiting application """
        while self.editor_list.get_size() > 0:
            reply = self.editor_list.close_current_editor()
            if reply == "cancel":
                break
        if self.editor_list.get_size() == 0:
            sys.exit(0)


    def run_module(self, event=None):
        """ Run the code : give the file name and code will be run from the source file """
        reply = self.editor_list.get_current_editor().maybesave_run()
        if (reply != "cancel"):
            file_name = self.editor_list.get_current_editor().long_title()
            self.console.run(file_name)


    # TODO: Continue ?
    def check_module(self, event=None):
        """ Check syntax : compilation """
        reply = self.editor_list.get_current_editor().maybesave_run()
        if (reply != "cancel"):
            self.console.check_syntax(self.editor_list.get_current_editor())


    # TODO: remove ?
    def run_source(self,event=None):
        file_name = self.editor_list.get_current_editor().long_title()
        self.console.runit(file_name)

if __name__ == "__main__":
    app = Application()
    app.run()  
