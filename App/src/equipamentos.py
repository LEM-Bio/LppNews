import flet as ft
from flet_toast import flet_toast
import uploadImgur as uploadImgur

class Equipamento(ft.ListView):
    def __init__(self, page: ft.Page, datanews, file_picker):
        super().__init__()
        self.page: ft.Page = page

        self.expand=1
        self.spacing=10
        self.padding=20
        self.auto_scroll=False

        self.dataNews = datanews
        self.file_picker = file_picker

        self.page.update()
        
    def getEquip(self, equip):
        return ft.Draggable(
                group="Equipamento",
                content=ft.DragTarget(
                    group="Equipamento",
                    content=ft.ExpansionTile(
                        title = ft.Row(
                                        [
                                            ft.Text(equip["cardTitle"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                            ft.IconButton(
                                                icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover equipamento",
                                                on_click=self.removeEquip,
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
                                                    ft.TextField(equip["image"]["url"], label="Url da imagem", on_change=lambda e: self.changeEquip(e, column='image', imageCol='url'), width=600),
                                                    ft.Image(
                                                                src=equip["image"]["url"],
                                                                width=500,
                                                            ),
                                                    ft.ElevatedButton("Escolher uma imagem...", on_click=lambda e: self.pickFiles(e)),
                                                    ft.TextField(equip["image"]["alt"], width=600, height=100, on_change=lambda e: self.changeEquip(e, column='image', imageCol='alt'), label="Alt da imagem")
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                            ),
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(equip['cardTitle'], on_change=lambda e: self.changeEquip(e, column='cardTitle'), label="Título do Card"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(equip['title'], on_change=lambda e: self.changeEquip(e, column='title'), label="Título"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(equip["content"], multiline=True, on_change=lambda e: self.changeEquip(e, column='content'), label="Conteúdo"),
                                                width=600, 
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                wrap=True,
                                alignment = ft.MainAxisAlignment.CENTER,
                            )
                        )]
                    ),
                    on_accept=self.drag_accept,
                    on_will_accept=self.drag_will_accept,
                    on_leave=self.drag_leave,
                ),
                content_feedback=ft.Text(equip["cardTitle"], text_align=ft.TextAlign.CENTER, size=23, color=ft.Colors.WHITE, weight=ft.FontWeight.NORMAL, spans=[], font_family="Consolas")
            )

    def equipReset(self):
        self.controls.clear()
        for i in range(len(self.dataNews['equipamentos'])):
            equipamento = self.dataNews['equipamentos'][i]
            self.controls.append( self.getEquip(equipamento) )
            
        self.page.update()

    def addEquip(self, e):
        novoEquip = {
                "title": "",
                "cardTitle": "",
                "content": "",
                "image": {
                    "url": "",
                    "alt": ""
                }
            }

        self.dataNews['equipamentos'].insert(0, novoEquip)
        self.equipReset()
        
        flet_toast.sucess(
            page=self.page,
            message="Novo equipamento adicionado",
            position="top_right",
            duration=3
        )

    def changeEquip(self, e, column, imageCol=''):
        if imageCol == '':
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent.parent)
        else:
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]
            if imageCol == '':
                self.dataNews['equipamentos'][index][column] = dataToChange
                return
                
            self.dataNews['equipamentos'][index][column][imageCol] = dataToChange

    def removeEquip(self, e):
        equipamento = e.control.parent.parent.parent.parent
        index = self.controls.index(equipamento)
        self.controls.remove(equipamento)
        self.dataNews['equipamentos'].pop(index)

        self.equipReset()
        flet_toast.sucess(
            page=self.page,
            message="Equipamento removido",
            position="top_right",
            duration=3
        )

    def drag_accept(self, e):
        # get draggable (source) control by its ID
        src = self.page.get_control(e.src_id)
        
        src.content.content, e.control.content = e.control.content, src.content.content

        indexSent = self.controls.index(src)
        indexGot = self.controls.index(e.control.parent)
        self.dataNews['equipamentos'][indexSent], self.dataNews['equipamentos'][indexGot] = self.dataNews['equipamentos'][indexGot], self.dataNews['equipamentos'][indexSent]

        # reset border
        e.control.content.color = None
        self.equipReset()

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

    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        path = e.files[0].path
        imgurUrl = uploadImgur.uploadImage(path)
        e.control.parent.parent.controls[0].value = imgurUrl
        
        imageTextField.value = imgurUrl
        index = self.controls.index(imageTextField.parent.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            self.dataNews['equipamentos'][index]['image']['url'] = imgurUrl
        self.equipReset()

    def pickFiles(self, e):
        global imageTextField
        imageTextField = e.control.parent.controls[0]
        
        self.file_picker.on_result = self.on_dialog_result
        self.file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)