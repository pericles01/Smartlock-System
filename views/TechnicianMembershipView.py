from kivymd.uix.screen import MDScreen

class TechnicianMembershipView(MDScreen):
    def __init__(self, **kwargs):
        super(TechnicianMembershipView, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.ids.manager.current = "setup"