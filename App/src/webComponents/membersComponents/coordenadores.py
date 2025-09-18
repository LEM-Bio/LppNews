import flet as ft
from webComponents.componentList import WebList
from webComponents.customTile import CustomTile

class Coordenador(WebList):
    def __init__(self, page: ft.Page, data={}, filepicker=ft.FilePicker()):
        super().__init__(
            name = "coordenadores",
            jsonSkeleton = {
                "name": "",
                "curriculo": "",
                "posicaoLab": "",
                "posicaoUni": "",
                "dep": "",
                "uni": ""
            },
            data=data,
            filepicker=filepicker,
            page=page
        )

        self.page.update()
        
    def getContent(self, content):
        tile = CustomTile(
                        title = ft.Row(
                                        [
                                            ft.Text(content["name"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                            ft.IconButton(
                                                icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover coordenador",
                                                on_click=self.removeContent,
                                                width=100,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                        controls=[ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(content['name'], on_change=lambda e: self.changeData(e, column='name'), label="Nome do Coordenador"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(content['posicaoLab'], on_change=lambda e: self.changeData(e, column='posicaoLab'), label="Posiçao no laboratorio"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(content['dep'], on_change=lambda e: self.changeData(e, column='dep'), label="Departamento"),
                                                width=600, 
                                                ),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(content['curriculo'], on_change=lambda e: self.changeData(e, column='curriculo'), label="Curriculo"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(content['posicaoUni'], on_change=lambda e: self.changeData(e, column='posicaoUni'), label="Posiçao na Universidade"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(content['uni'], on_change=lambda e: self.changeData(e, column='uni'), label="Universidade"),
                                                width=600, 
                                                ),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                vertical_alignment = ft.MainAxisAlignment.CENTER,
                                wrap=True,
                            )
                        )]
                    )
        
        tile.on_change = lambda e : self.expandState(e, tile)
        return tile