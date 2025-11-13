import flet as ft
import datetime
from webComponents.componentList import WebList
from webComponents.customTile import CustomTile

class Publicacao(WebList):
    def __init__(self, page: ft.Page, data={}, filepicker=ft.FilePicker()):
        super().__init__(
            name = "publicados",
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
        tile = CustomTile(
                        title = ft.Row(
                                        [
                                            ft.Text(content["title"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                            ft.IconButton(
                                                icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover publicação",
                                                on_click=self.removeContent,
                                                width=100,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                        controls=[ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                                [
                                                    ft.TextField(content["image"]["url"], label="Url da imagem", on_blur=lambda e: self.changeData(e, column='image', imageCol='url', content=content), width=600),
                                                    ft.Image(
                                                                src=content["image"]["url"],
                                                                width=500,
                                                            ),
                                                    ft.ElevatedButton("Escolher uma imagem...", on_click=lambda e: self.pickFiles(e)),
                                                    ft.TextField(content["image"]["alt"], width=600, height=100, on_blur=lambda e: self.changeData(e, column='image', imageCol='alt', content=content), label="Alt da imagem")
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                            ),
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(content['title'], on_blur=lambda e: self.changeData(e, column='title', content=content), label="Título"),
                                                width=600, 
                                                ),
                                            ft.Row(
                                                controls=[
                                                    ft.ListTile(
                                                        title=ft.TextField(content['publishDate'], read_only=True, label="Data de publicaçao"), 
                                                        dense=True,
                                                        width=600, 
                                                        ),
                                                    ft.ElevatedButton(
                                                        "Escolher data",
                                                        icon=ft.Icons.CALENDAR_MONTH,
                                                        on_click=lambda e: self.page.open(
                                                            ft.DatePicker(
                                                                first_date=datetime.datetime(year=1900, month=10, day=1),
                                                                last_date=datetime.datetime(year=2200, month=12, day=31),
                                                                on_change=lambda e: self.changeData(e, column='publishDate', value=e.control.value.strftime('%d/%m/%Y'), content=content)
                                                            )
                                                        ),
                                                    ),
                                                ],
                                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                                alignment=ft.MainAxisAlignment.CENTER
                                            ),
                                            ft.ListTile(
                                                title=ft.TextField(content["content"], multiline=True, on_blur=lambda e: self.changeData(e, column='content', content=content), label="Conteúdo"),
                                                width=600, 
                                            ),
                                            ft.ListTile(
                                                title=ft.TextField(content["link"], on_blur=lambda e: self.changeData(e, column='link', content=content), label="Link da publicação"),
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
        
        tile.on_change = lambda e : self.expandState(e, tile)
        return tile