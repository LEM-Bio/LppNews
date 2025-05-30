import flet as ft
from flet_toast import flet_toast
import uploadImgur as uploadImgur

class Noticia(ft.ListView):
    def __init__(self, page: ft.Page, datanews, filepicker):
        super().__init__()
        self.page: ft.Page = page

        self.expand=1
        self.spacing=10
        self.padding=20
        self.auto_scroll=False

        self.dataNews = datanews
        self.filepicker = filepicker

        self.page.update()
        
    def getNoticia(self, noticia):
        return ft.Draggable(
            group="Noticia",
        content_feedback=ft.Text(noticia["title"], text_align=ft.TextAlign.CENTER, size=23, color=ft.Colors.WHITE, weight=ft.FontWeight.NORMAL, spans=[], font_family="Consolas"),
        content=ft.DragTarget(
                group="Noticia",
                content=ft.ExpansionTile(
                    title = ft.Row(
                                    [
                                        ft.Text(noticia["title"], text_align=ft.TextAlign.LEFT, size=23, width=self.page.width*0.6, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.IconButton(
                                            icon=ft.Icons.INDETERMINATE_CHECK_BOX,
                                            icon_color="blue400",
                                            icon_size=30,
                                            tooltip="Remover noticia",
                                            on_click=self.removeNot,
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
                                                ft.TextField(noticia["image"]["url"], label="Url da imagem", on_change=lambda e: self.changeData(e, column='image', imageCol='url'), width=600),
                                                ft.Image(
                                                            src=noticia["image"]["url"],
                                                            width=500,
                                                        ),
                                                ft.ElevatedButton("Escolher uma imagem...", on_click=lambda e: self.pickFiles(e)),
                                                ft.TextField(noticia["image"]["alt"], width=600, height=100, on_change=lambda e: self.changeData(e, column='image', imageCol='alt'), label="Alt da imagem")
                                            ],
                                            alignment=ft.MainAxisAlignment.START,
                                            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                        ),
                                ft.Column(
                                    [
                                        ft.ListTile(
                                            title=ft.TextField(noticia['title'], on_change=lambda e: self.changeData(e, column='title'), label="Título"),
                                            width=600, 
                                            ),
                                        ft.ListTile(
                                            title=ft.TextField(noticia['publishDate'], on_change=lambda e: self.changeData(e, column='publishDate'), label="Data"), 
                                            dense=True,
                                            width=600, 
                                            ),
                                        ft.ListTile(
                                            title=ft.TextField(noticia["content"], multiline=True, on_change=lambda e: self.changeData(e, column='content'), label="Conteúdo"),
                                            width=600, 
                                        ),
                                        ft.ListTile(
                                            title=ft.TextField(noticia["link"], on_change=lambda e: self.changeData(e, column='link'), label="Link da notícia"),
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
            )
        )

    def newsReset(self):
        self.controls.clear()
        for i in range(len(self.dataNews['noticias'])):
            noticia = self.dataNews['noticias'][i]
            self.controls.append( self.getNoticia(noticia) )

        self.page.update()

    def addNot(self, e):
        novaNoticia = {
                "title": "",
                "content": "",
                "image": {
                    "url": "",
                    "alt": ""
                },
                "publishDate": "",
                "link": ""
            }

        self.dataNews['noticias'].insert(0, novaNoticia)
        self.newsReset()
        
        flet_toast.sucess(
            page=self.page,
            message="Nova notícia adicionada",
            position="top_right",
            duration=3
        )

    def changeData(self, e, column, imageCol=''):
        if imageCol == '':
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent.parent)
        else:
            index = self.controls.index(e.control.parent.parent.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]
            if imageCol == '':
                self.dataNews['noticias'][index][column] = dataToChange
                return
                
            self.dataNews['noticias'][index][column][imageCol] = dataToChange

    def removeNot(self, e):
        noticia = e.control.parent.parent.parent.parent
        index = self.controls.index(noticia)
        self.controls.remove(noticia)
        self.dataNews['noticias'].pop(index)

        self.newsReset()
        flet_toast.sucess(
            page=self.page,
            message="Notícia removida",
            position="top_right",
            duration=3
        )

    def drag_accept(self, e):
        # get draggable (source) control by its ID
        src = self.page.get_control(e.src_id)
        
        src.content.content, e.control.content = e.control.content, src.content.content

        indexSent = self.controls.index(src)
        indexGot = self.controls.index(e.control.parent)
        self.dataNews['noticias'][indexSent], self.dataNews['noticias'][indexGot] = self.dataNews['noticias'][indexGot], self.dataNews['noticias'][indexSent]

        # reset border
        e.control.content.color = None
        self.newsReset()

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
            self.dataNews['noticias'][index]['image']['url'] = imgurUrl
        self.newsReset()

    def pickFiles(self, e):
        global imageTextField
        imageTextField = e.control.parent.controls[0]
        
        self.filepicker.on_result = self.on_dialog_result
        self.filepicker.pick_files(allow_multiple=False)