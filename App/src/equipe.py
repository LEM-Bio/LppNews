import flet as ft
from flet_toast import flet_toast

class Equipe(ft.ListView):
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
                group="Tecnicos",
                content=ft.DragTarget(
                    group="Tecnicos",
                    content=ft.ExpansionTile(
                        title = ft.Row(
                                        [
                                            ft.Text(coord["name"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                            ft.IconButton(
                                                icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover tecnico",
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
                                                title=ft.TextField(coord['dep'], on_change=lambda e: self.changeCoord(e, column='dep'), label="Departamento"),
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
        for i in range(len(self.dataNews['eqTecnica'])):
            coordenador = self.dataNews['eqTecnica'][i]
            self.controls.append( self.getCoord(coordenador) )
            
        self.page.update()

    def addCoord(self, e):
        novoCoord = {
                "name": "",
                "curriculo": "",
                "dep": "",
                "uni": ""
            }

        self.dataNews['eqTecnica'].insert(0, novoCoord)
        self.coordReset()
        
        flet_toast.sucess(
            page=self.page,
            message="Novo tecnico adicionado",
            position="top_right",
            duration=3
        )

    def changeCoord(self, e, column, imageCol=''):
        if imageCol == '':
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent.parent)
        else:
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]
            if imageCol == '':
                self.dataNews['eqTecnica'][index][column] = dataToChange
                return
                
            self.dataNews['eqTecnica'][index][column][imageCol] = dataToChange

    def removeCoord(self, e):
        coordenador = e.control.parent.parent.parent.parent
        index = self.controls.index(coordenador)
        self.controls.remove(coordenador)
        self.dataNews['eqTecnica'].pop(index)

        self.coordReset()
        flet_toast.sucess(
            page=self.page,
            message="Tecnico removido",
            position="top_right",
            duration=3
        )

    def drag_accept(self, e):
        # get draggable (source) control by its ID
        src = self.page.get_control(e.src_id)
        
        src.content.content, e.control.content = e.control.content, src.content.content

        indexSent = self.controls.index(src)
        indexGot = self.controls.index(e.control.parent)
        self.dataNews['eqTecnica'][indexSent], self.dataNews['eqTecnica'][indexGot] = self.dataNews['eqTecnica'][indexGot], self.dataNews['eqTecnica'][indexSent]

        # reset border
        e.control.content.color = None
        self.coordReset()

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