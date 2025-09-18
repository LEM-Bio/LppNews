import flet as ft
from webComponents.componentList import WebList
from webComponents.customTile import CustomTile
from utils.toast import *

class Artigo(WebList):
    def __init__(self, page: ft.Page, data):
        super().__init__(
            name = "",
            jsonSkeleton = {},
            data=data,
            page=page
        )

        self.page.update()

    def getContent(self, content):
        tile = CustomTile(
                    title = ft.Row(
                                    [
                                        ft.Text(f'{content["id"]} {content["ano"]} {content["texto"]}', text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.IconButton(
                                            icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                            icon_color="blue400",
                                            icon_size=30,
                                            tooltip="Remover artigo",
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
                                            title=ft.TextField(content['ano'], on_change=lambda e: self.changeData(e, column='ano'), label="Ano", input_filter = ft.NumbersOnlyInputFilter()),
                                            width=600, 
                                            ),
                                        ft.ListTile(
                                            title=ft.TextField(content['texto'], on_change=lambda e: self.changeData(e, column='texto'), label="Texto"),
                                            width=600, 
                                            ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Column(
                                    [
                                        ft.ListTile(
                                            title=ft.TextField(content['link'], on_change=lambda e: self.changeData(e, column='link'), label="Link"),
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
    
    def componentReset(self):
        self.controls.clear()
        for i in range(len(self.data)):
            artigo = self.data.iloc[i].to_dict()
            artigo["id"] = i + 1
            self.controls.append( self.getContent(artigo) )
        self.data.reset_index(drop=True, inplace=True)
            

    def addContent(self, e):
        newContent = {
            "id": len(self.data)+1,
            "ano": "",
            "texto": "",
            "link": ""
        }

        self.data.loc[len(self.data)] = newContent
        self.componentReset()

        self.toast_manager.show_toast(
            toast_type=ToastType.SUCCESS,
            text=f"Novo item adicionado"
        )
        self.page.update()

    def removeContent(self, e):
        artigo = e.control.parent.parent
        index = self.controls.index(artigo)
        self.controls.remove(artigo)
        print(self.data.shape[0])
        self.data.drop(index, axis=0, inplace=True)
        print(self.data.shape[0])

        self.componentReset()
        self.page.update()

    def changeData(self, e, column, imageCol=''):
        index = self.controls.index(e.control.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]

            self.data[column][index] = dataToChange
            return
        
        self.page.update()

    def handle_reorder(self, e: ft.OnReorderEvent):
        b, c = self.data.iloc[e.old_index].copy(), self.data.iloc[e.new_index].copy()
        b[0] = e.new_index + 1
        c[0] = e.old_index + 1
        self.data.iloc[e.old_index], self.data.iloc[e.new_index] = c, b
        
        self.componentReset()
        self.page.update()