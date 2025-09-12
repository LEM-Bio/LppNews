import flet as ft

class CustomTile(ft.ExpansionTile):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.affinity=ft.TileAffinity.LEADING
        self.expanded = self.initially_expanded
        self.on_change = self.expand #FIXME

    def expand(self):
        print("expandiu")
        print(not self.expanded)
        self.expanded = not self.expanded
    