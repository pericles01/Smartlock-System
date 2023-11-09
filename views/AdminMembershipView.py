import os
from kivymd.toast import toast
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout


class AdminMembershipView(MDFloatLayout):
    def __init__(self, **kwargs):
        super(AdminMembershipView, self).__init__(**kwargs)

        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path, selector="file", ext=[".csv", ".json"]#,preview=True
        )

    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        #self.file_manager.show_disks()
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        toast(os.path.basename(path))

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()