import flet as ft

class Comite(ft.ListView):
    def __init__(self, page: ft.Page, datanews, file_picker):
        super().__init__()
        self.page: ft.Page = page

        self.expand=1
        self.spacing=10
        self.padding=20
        self.scroll = ft.ScrollMode.HIDDEN

        self.dataNews = datanews
        self.file_picker = file_picker

        self.page.update()
        
    def getCoord(self, coord):
        return ft.Draggable(
                group="Comite de Usuarios",
                content=ft.DragTarget(
                    group="Comite de Usuarios",
                    content=ft.ExpansionTile(
                        title = ft.Row(
                                        [
                                            ft.Text(coord["name"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                            ft.IconButton(
                                                icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover usuario",
                                                on_click=self.removeCoord,
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
                                                title=ft.TextField(coord['name'], on_change=lambda e: self.changeCoord(e, column='name'), label="Nome do Tecnico"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(coord['posicao'], on_change=lambda e: self.changeCoord(e, column='posicao'), label="Posicao"),
                                                width=600, 
                                                ),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(coord['curriculo'], on_change=lambda e: self.changeCoord(e, column='curriculo'), label="Curriculo"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(coord['dep'], on_change=lambda e: self.changeCoord(e, column='dep'), label="Departamento"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(coord['uni'], on_change=lambda e: self.changeCoord(e, column='uni'), label="Universidade"),
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
                content_feedback=ft.Text(coord["name"], text_align=ft.TextAlign.CENTER, size=23, color=ft.Colors.WHITE, weight=ft.FontWeight.NORMAL, spans=[], font_family="Consolas")
            )

    def coordReset(self):
        self.controls.clear()
        for i in range(len(self.dataNews['comite'])):
            coordenador = self.dataNews['comite'][i]
            self.controls.append( self.getCoord(coordenador) )
            
        self.page.update()

    def addCoord(self, e):
        novoCoord = {
                "name": "",
                "curriculo": "",
                "posicao": "",
                "dep": "",
                "uni": ""
            }

        self.dataNews['comite'].insert(0, novoCoord)
        self.coordReset()

    def changeCoord(self, e, column, imageCol=''):
        if imageCol == '':
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent.parent)
        else:
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]
            if imageCol == '':
                self.dataNews['comite'][index][column] = dataToChange
                return
                
            self.dataNews['comite'][index][column][imageCol] = dataToChange

    def removeCoord(self, e):
        coordenador = e.control.parent.parent.parent.parent
        index = self.controls.index(coordenador)
        self.controls.remove(coordenador)
        self.dataNews['comite'].pop(index)

        self.coordReset()

    def drag_accept(self, e):
        # get draggable (source) control by its ID
        src = self.page.get_control(e.src_id)
        
        src.content.content, e.control.content = e.control.content, src.content.content

        indexSent = self.controls.index(src)
        indexGot = self.controls.index(e.control.parent)
        self.dataNews['comite'][indexSent], self.dataNews['comite'][indexGot] = self.dataNews['comite'][indexGot], self.dataNews['comite'][indexSent]

        # reset border
        e.control.content.color = None
        self.coordReset()

        self.page.update()

    def drag_will_accept(self, e):
        e.control.content.color = ft.Colors.BLUE_600
        e.control.update()

    def drag_leave(self, e):
        e.control.content.color = None
        e.control.update()