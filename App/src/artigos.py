import flet as ft
from flet_toast import flet_toast
import pandas as pd

class Artigo(ft.ListView):
    def __init__(self, page: ft.Page, data):
        super().__init__()
        self.page: ft.Page = page

        self.expand=1
        self.spacing=10
        self.padding=20
        self.auto_scroll=False

        self.data = data

        self.page.update()
        
    def getArtigo(self, artigo):
        return ft.Draggable(
                group="Artigo",
                content=ft.DragTarget(
                    group="Artigo",
                    content=ft.ExpansionTile(
                        title = ft.Row(
                                        [
                                            ft.Text(f'{artigo["id"]} {artigo["ano"]} {artigo["texto"]}', text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                            ft.IconButton(
                                                icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover artigo",
                                                on_click=self.removeArtigo,
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
                                                title=ft.TextField(artigo['ano'], on_change=lambda e: self.changeArtigo(e, column='ano'), label="Ano"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(artigo['texto'], on_change=lambda e: self.changeArtigo(e, column='texto'), label="Texto"),
                                                width=600, 
                                                ),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(artigo['link'], on_change=lambda e: self.changeArtigo(e, column='link'), label="Link"),
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
                    ),
                    on_accept=self.drag_accept,
                    on_will_accept=self.drag_will_accept,
                    on_leave=self.drag_leave,
                ),
                content_feedback=ft.Text(artigo["id"], text_align=ft.TextAlign.CENTER, size=23, color=ft.Colors.WHITE, weight=ft.FontWeight.NORMAL, spans=[], font_family="Consolas")
            )

    def artigoReset(self):
        self.controls.clear()
        for i in range(len(self.data)):
            artigo = self.data.iloc[i].to_dict()
            self.controls.append( self.getArtigo(artigo) )
            
        self.page.update()

    def addArtigo(self, e):
        novoArtigo = {
                "id": len(self.data)+1,
                "ano": "",
                "texto": "",
                "link": ""
            }

        self.data.loc[len(self.data)] = novoArtigo
        self.artigoReset()
        
        flet_toast.sucess(
            page=self.page,
            message="Novo artigo adicionado",
            position="top_right",
            duration=3
        )

    def changeArtigo(self, e, column):
        index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]

            self.data[column][index] = dataToChange
            return

    def removeArtigo(self, e):
        artigo = e.control.parent.parent.parent.parent
        index = self.controls.index(artigo)
        self.controls.remove(artigo)
        self.data.drop(index,axis=0,inplace=True)

        self.artigoReset()
        flet_toast.sucess(
            page=self.page,
            message="Artigo removido",
            position="top_right",
            duration=3
        )

    def drag_accept(self, e):
        # get draggable (source) control by its ID
        src = self.page.get_control(e.src_id)
        
        src.content.content, e.control.content = e.control.content, src.content.content

        indexSent = self.controls.index(src)
        indexGot = self.controls.index(e.control.parent)

        b, c = self.data.iloc[indexSent].copy(), self.data.iloc[indexGot].copy()
        b[0] = indexGot + 1
        c[0] = indexSent + 1
        self.data.iloc[indexSent], self.data.iloc[indexGot] = c, b

        # reset border
        e.control.content.color = None
        self.artigoReset()

        flet_toast.sucess(
            page=self.page,
            message="Ordem atualizada",
            position="top_right",
            duration=3
        )

        self.page.update()

    def drag_will_accept(self, e):
        e.control.content.color = ft.Colors.BLUE_600
        e.control.update()

    def drag_leave(self, e):
        e.control.content.color = None
        e.control.update()