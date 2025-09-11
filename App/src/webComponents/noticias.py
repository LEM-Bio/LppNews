import flet as ft
from webComponents.componentList import WebList

class Noticia(WebList):
    def __init__(self, page: ft.Page, data={}, filepicker=ft.FilePicker()):
        super().__init__(
            name = "noticias",
            jsonSkeleton = {
                "title": "",
                "content": "",
                "image": {
                    "url": "",
                    "alt": ""
                },
                "publishDate": "",
                "link": ""
            },
            data=data,
            filepicker=filepicker,
            page=page
        )

        self.page.update()
        
    def getContent(self, content):
        return ft.ExpansionTile(
                    title = ft.Row(
                                    [
                                        ft.Text(content["title"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.IconButton(
                                            icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                            icon_color="blue400",
                                            icon_size=30,
                                            tooltip=f"Remover item",
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
                                                ft.TextField(content["image"]["url"], label="Url da imagem", on_change=lambda e: self.changeData(e, column='image', imageCol='url'), width=600),
                                                ft.Image(
                                                            src=content["image"]["url"],
                                                            width=500,
                                                        ),
                                                ft.ElevatedButton("Escolher uma imagem...", on_click=lambda e: self.pickFiles(e)),
                                                ft.TextField(content["image"]["alt"], width=600, height=100, on_change=lambda e: self.changeData(e, column='image', imageCol='alt'), label="Alt da imagem")
                                            ],
                                            alignment=ft.MainAxisAlignment.START,
                                            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                        ),
                                ft.Column(
                                    [
                                        ft.ListTile(
                                            title=ft.TextField(content['title'], on_change=lambda e: self.changeData(e, column='title'), label="Título"),
                                            width=600, 
                                            ),
                                        ft.ListTile(
                                            title=ft.TextField(content['publishDate'], on_change=lambda e: self.changeData(e, column='publishDate'), label="Data"), 
                                            dense=True,
                                            width=600, 
                                            ),
                                        ft.ListTile(
                                            title=ft.TextField(content["content"], multiline=True, on_change=lambda e: self.changeData(e, column='content'), label="Conteúdo"),
                                            width=600, 
                                        ),
                                        ft.ListTile(
                                            title=ft.TextField(content["link"], on_change=lambda e: self.changeData(e, column='link'), label=f"Link do item"),
                                            width=600, 
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            wrap=True,
                            alignment = ft.MainAxisAlignment.CENTER,
                        )
                    )]
                )