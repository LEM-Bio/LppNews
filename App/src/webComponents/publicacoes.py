import flet as ft
import utils.uploadImgur as uploadImgur

class Publicacao(ft.ListView):
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
        
    def getPubli(self, pub):
        return ft.Draggable(
                group="Publicação",
                content=ft.DragTarget(
                    group="Publicação",
                    content=ft.ExpansionTile(
                        title = ft.Row(
                                        [
                                            ft.Text(pub["title"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                            ft.IconButton(
                                                icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover publicação",
                                                on_click=self.removePub,
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
                                                    ft.TextField(pub["image"]["url"], label="Url da imagem", on_change=lambda e: self.changePub(e, column='image', imageCol='url'), width=600),
                                                    ft.Image(
                                                                src=pub["image"]["url"],
                                                                width=500,
                                                            ),
                                                    ft.ElevatedButton("Escolher uma imagem...", on_click=lambda e: self.pickFiles(e)),
                                                    ft.TextField(pub["image"]["alt"], width=600, height=100, on_change=lambda e: self.changePub(e, column='image', imageCol='alt'), label="Alt da imagem")
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                            ),
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(pub['title'], on_change=lambda e: self.changePub(e, column='title'), label="Título"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(pub['publishDate'], on_change=lambda e: self.changePub(e, column='publishDate'), label="Data"), 
                                                dense=True,
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(pub["content"], multiline=True, on_change=lambda e: self.changePub(e, column='content'), label="Conteúdo"),
                                                width=600, 
                                            ),
                                            ft.ListTile(
                                                title=ft.TextField(pub["link"], on_change=lambda e: self.changePub(e, column='link'), label="Link da publicação"),
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
                    ),
                    on_accept=self.drag_accept,
                    on_will_accept=self.drag_will_accept,
                    on_leave=self.drag_leave,
                ),
                content_feedback=ft.Text(pub["title"], text_align=ft.TextAlign.CENTER, size=23, color=ft.Colors.WHITE, weight=ft.FontWeight.NORMAL, spans=[], font_family="Consolas")
            )

    def pbsReset(self):
        self.controls.clear()
        for i in range(len(self.dataNews['publicados'])):
            publicacao = self.dataNews['publicados'][i]
            self.controls.append( self.getPubli(publicacao) )
            
        self.page.update()

    def addPub(self, e):
        novaPub = {
                "title": "",
                "content": "",
                "image": {
                    "url": "",
                    "alt": ""
                },
                "publishDate": "",
                "link": ""
            }

        self.dataNews['publicados'].insert(0, novaPub)
        self.pbsReset()

    def changePub(self, e, column, imageCol=''):
        if imageCol == '':
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent.parent)
        else:
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]
            if imageCol == '':
                self.dataNews['publicados'][index][column] = dataToChange
                return
                
            self.dataNews['publicados'][index][column][imageCol] = dataToChange

    def removePub(self, e):
        publicacao = e.control.parent.parent.parent.parent
        index = self.controls.index(publicacao)
        self.controls.remove(publicacao)
        self.dataNews['publicados'].pop(index)

        self.pbsReset()

    def drag_accept(self, e):
        # get draggable (source) control by its ID
        src = self.page.get_control(e.src_id)
        
        src.content.content, e.control.content = e.control.content, src.content.content

        indexSent = self.controls.index(src)
        indexGot = self.controls.index(e.control.parent)
        self.dataNews['publicados'][indexSent], self.dataNews['publicados'][indexGot] = self.dataNews['publicados'][indexGot], self.dataNews['publicados'][indexSent]

        # reset border
        e.control.content.color = None
        self.pbsReset()

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
            self.dataNews['publicados'][index]['image']['url'] = imgurUrl
        self.pbsReset()

    def pickFiles(self, e):
        global imageTextField
        imageTextField = e.control.parent.controls[0]
        
        self.file_picker.on_result = self.on_dialog_result
        self.file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)