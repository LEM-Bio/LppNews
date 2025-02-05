import flet as ft
import json
from copy import deepcopy
from flet_toast import flet_toast
import os
import uploadImgur
import git
import shutil
import config
import pynpm as npm
import paramiko
from connection import MySFTPClient

output = os.getcwd()
shutil.rmtree(os.path.join(f'{output}', 'LembioWebsite'), ignore_errors=True)
print(os.path.join(f'{output}', 'LembioWebsite'))

git.Git(output).clone(f'https://{config.secret_token}@github.com/LEM-Bio/LembioWebsite.git', "--branch=main")

paginaPath = os.path.join(f'{output}', 'LembioWebsite')
repo = git.Repo(paginaPath)
repo.git.init()
repo.config_writer().set_value("user", "name", "mousedesvio").release()
repo.config_writer().set_value("user", "email", "redbrickcar2@gmail.com").release()
repo.git.remote("set-url", "origin", f"https://{config.secret_token}@github.com/LEM-Bio/LembioWebsite.git")

#Noticias
jsonPath = os.path.join(f'{output}', 'LembioWebsite', 'src', 'data', 'components-mock.json')

fNews = open(jsonPath, "r")
fNews2 = open(jsonPath, "r")

global dataNewsOriginal
global dataNews
dataNewsOriginal = json.load(fNews)
fNews.close()

dataNews = json.load(fNews2)
fNews2.close()

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Aplicativo para atualização do Website LEMbio"
    page.window.min_height = 300
    page.window.min_width = 450

    global dataNewsOriginal
    global dataNews

    #DEFINIR O QUE APARECE NA TELA
    lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=False)
    botoes = ft.ResponsiveRow()
    
    #FECHAR JSON ANTES DE FECHAR APP
    def handle_window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)

    page.window.prevent_close = True
    page.window.on_event = handle_window_event

    def handle_yes(e):
        wNews = open(jsonPath, "w")

        json.dump(dataNewsOriginal, wNews, indent=2)
        wNews.close()
        shutil.rmtree(os.path.join(f'{output[:-1]}', 'LembioWebsite'), ignore_errors=True)
        page.window.destroy()

    def handle_no(e):
        page.close(confirm_dialog)

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirme"),
        content=ft.Text("Voce realmente que sair?"),
        actions=[
            ft.ElevatedButton("Sim", on_click=handle_yes),
            ft.OutlinedButton("Nao", on_click=handle_no),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def saveYes(e, closeDiag = True):
        global dataNewsOriginal
        dataNewsOriginal = {}

        dataNewsOriginal = deepcopy(dataNews)

        wNews = open(jsonPath, "w")

        json.dump(dataNewsOriginal, wNews, indent=2)
        wNews.close()

        try:
            repo.git.add(".")
            repo.git.commit("-m", "Change news")
            repo.git.push("-u", "origin", "main")
        except:
            flet_toast.error(
                page=page,
                message="Erro ao conectar no github",
                position=flet_toast.Position.TOP_LEFT,
                duration=3
            )
        
        if closeDiag:
            page.close(confirmSave_dialog)
        newsReset()

    def saveNo(e):
        page.close(confirmSave_dialog)

    confirmSave_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirme"),
        content=ft.Text("Voce realmente quer salvar os dados?"),
        actions=[
            ft.ElevatedButton("Sim", on_click=saveYes),
            ft.OutlinedButton("Nao", on_click=saveNo),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def saveData(e):
        page.open(confirmSave_dialog)


    def newsReset():
        lv.controls.clear()
        for i in range(len(dataNews['noticias'])):
            noticia = dataNews['noticias'][i]
            lv.controls.append( getNoticia(i, noticia) )
            
        page.update()

    def discardYes(e):
        global dataNews
        dataNews = {}
        dataNews = deepcopy(dataNewsOriginal)
        
        newsReset()
        
        page.close(confirmDiscard_dialog)

    def discardNo(e):
        page.close(confirmDiscard_dialog)

    confirmDiscard_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirme"),
        content=ft.Text("Voce realmente quer descartar as mudanças?"),
        actions=[
            ft.ElevatedButton("Sim", on_click=discardYes),
            ft.OutlinedButton("Nao", on_click=discardNo),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def discardData(e):
        page.open(confirmDiscard_dialog)


    def addNot(e):
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

        dataNews['noticias'].insert(0, novaNoticia)
        newsReset()
        
        flet_toast.sucess(
            page=page,
            message="Nova notícia adicionada",
            position=flet_toast.Position.TOP_LEFT,
            duration=3
        )
    
    def trySend(e):
        user = e.control.parent.content.controls[0].value
        password = e.control.parent.content.controls[1].value
        saveYes(e, False)

        defaultContent = insertLogin_dialog.content.controls.copy()
        defaultActions = insertLogin_dialog.actions.copy()
        defaultTitle = insertLogin_dialog.title

        insertLogin_dialog.content.controls.clear()
        insertLogin_dialog.actions.clear()
        insertLogin_dialog.title = ft.Text("Carregando arquivos...")
        insertLogin_dialog.update()
        insertLogin_dialog.content = ft.Container(height = 50, alignment=ft.alignment.center)
        insertLogin_dialog.content.content = (ft.ProgressRing(width=30, height=30, stroke_width = 3))

        insertLogin_dialog.update()

        pkg = npm.NPMPackage(os.path.join(f'{paginaPath}', 'package.json'), shell=True)
        pkg.install()
        pkg.run_script('build')

        remote_path = "/usr/share/nginx/html"

        transport = paramiko.Transport(('172.22.161.213', 22))
        transport.connect(username=user, password=password)
        sftp = MySFTPClient.from_transport(transport)
        sftp.put_dir(os.path.join(f"{paginaPath}", "build"), remote_path)
        sftp.close()
        
        insertLogin_dialog.content = ft.Column(defaultContent.copy(), height=100)
        insertLogin_dialog.actions = defaultActions.copy()
        insertLogin_dialog.title = defaultTitle

        page.close(insertLogin_dialog)
        insertLogin_dialog.update()
        

    def closeLogin(e):
        page.close(insertLogin_dialog)

    insertLogin_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Text("Insira seus dados do servidor"),
            ft.IconButton(icon=ft.icons.CLOSE, on_click=closeLogin)
            ]),
        content=ft.Column([
            ft.TextField(label="Usuario"),
            ft.TextField(label="Senha", password=True)
        ], height=100),
        actions=[
            ft.ElevatedButton("Enviar", on_click=trySend),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def sendData(e):
        page.open(insertLogin_dialog)

    #Definindo os botoes de salvamento, descarte, adiçao de noticias e envio ao servidor
    botoes.controls.append(
        ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Adicionar noticia",
                        on_click=addNot
                    ),
                    ft.ElevatedButton("Salvar", on_click=saveData, bgcolor="green", color="white"),
                    ft.ElevatedButton("Descartar", on_click=discardData, bgcolor="red", color="white"),
                    ft.IconButton(
                        icon=ft.icons.SEND,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Enviar dados salvos ao servidor",
                        on_click=sendData,
                    )
                ],
                alignment="CENTER",
            )
    )

    def changeData(e, column, imageCol=''):
        if imageCol == '':
            index = lv.controls.index(e.control.parent.parent.parent.parent.parent.parent.parent)
        else:
            index = lv.controls.index(e.control.parent.parent.parent.parent.parent.parent)

        if len(lv.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]
            if imageCol == '':
                dataNews['noticias'][index][column] = dataToChange
                return
                
            dataNews['noticias'][index][column][imageCol] = dataToChange
        

    def removeNot(e):
        noticia = e.control.parent.parent.parent.parent
        index = lv.controls.index(noticia)
        lv.controls.remove(noticia)
        dataNews['noticias'].pop(index)

        newsReset()
        flet_toast.sucess(
            page=page,
            message="Notícia removida",
            position=flet_toast.Position.TOP_LEFT,
            duration=3
        )

    def drag_accept(e):
        # get draggable (source) control by its ID
        src = page.get_control(e.src_id)
        
        src.content.content, e.control.content = e.control.content, src.content.content

        indexSent = lv.controls.index(src)
        indexGot = lv.controls.index(e.control.parent)
        dataNews['noticias'][indexSent], dataNews['noticias'][indexGot] = dataNews['noticias'][indexGot], dataNews['noticias'][indexSent]

        # reset border
        e.control.content.color = None
        newsReset()

        flet_toast.sucess(
            page=page,
            message="Ordem atualizada",
            position=flet_toast.Position.TOP_LEFT,
            duration=3
        )

        page.update()

    def drag_will_accept(e):
        e.control.content.color = ft.colors.BLUE_600
        e.control.update()

    def drag_leave(e):
        e.control.content.color = None
        e.control.update()

    global imageTextField
    imageTextField = ft.TextField()

    def on_dialog_result(e: ft.FilePickerResultEvent):
        print(e.files[0].path)
        path = e.files[0].path
        imgurUrl = uploadImgur.uploadImage(path)
        e.control.parent.parent.controls[0].value = imgurUrl
        
        imageTextField.value = imgurUrl
        index = lv.controls.index(imageTextField.parent.parent.parent.parent.parent.parent)

        if len(lv.controls) > index:
            dataNews['noticias'][index]['image']['url'] = imgurUrl
        newsReset()

    def pickFiles(e):
        file_picker.pick_files(allow_multiple=False)
        global imageTextField
        imageTextField = e.control.parent.controls[0]

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()

    def getNoticia(i, noticia):
        return ft.Draggable(
                group="Noticia",
                content=ft.DragTarget(
                    group="Noticia",
                    content=ft.ExpansionTile(
                        title = ft.Row(
                                        [
                                            ft.Text(f"Noticia {i}", text_align=ft.TextAlign.CENTER, size=23, width=130),
                                            ft.IconButton(
                                                icon=ft.icons.INDETERMINATE_CHECK_BOX,
                                                icon_color="blue400",
                                                icon_size=30,
                                                tooltip="Remover noticia",
                                                on_click=removeNot,
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
                                                    ft.TextField(noticia["image"]["url"], label="Url da imagem", on_change=lambda e: changeData(e, column='image', imageCol='url'), width=600),
                                                    ft.Image(
                                                                src=noticia["image"]["url"],
                                                                width=500,
                                                            ),
                                                    ft.ElevatedButton("Escolher uma imagem...", on_click=lambda e: pickFiles(e)),
                                                    ft.TextField(noticia["image"]["alt"], width=600, height=100, on_change=lambda e: changeData(e, column='image', imageCol='alt'), label="Alt da imagem")
                                                ],
                                                alignment=ft.MainAxisAlignment.START,
                                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                            ),
                                    ft.Column(
                                        [
                                            ft.ListTile(
                                                title=ft.TextField(noticia['title'], on_change=lambda e: changeData(e, column='title'), label="Título"),
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(noticia['publishDate'], on_change=lambda e: changeData(e, column='publishDate'), label="Data"), 
                                                dense=True,
                                                width=600, 
                                                ),
                                            ft.ListTile(
                                                title=ft.TextField(noticia["content"], multiline=True, on_change=lambda e: changeData(e, column='content'), label="Conteúdo"),
                                                width=600, 
                                            ),
                                            ft.ListTile(
                                                title=ft.TextField(noticia["link"], on_change=lambda e: changeData(e, column='link'), label="Link da notícia"),
                                                width=600, 
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.START,
                                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                                    ),
                                ],
                                wrap=True,
                                alignment = ft.MainAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.symmetric(vertical=10),
                        )]
                    ),
                    on_accept=drag_accept,
                    on_will_accept=drag_will_accept,
                    on_leave=drag_leave,
                ),
                content_feedback=ft.Text(f"Notícia {i}", text_align=ft.TextAlign.CENTER, size=23, color=ft.colors.WHITE, weight=ft.FontWeight.NORMAL, spans=[], font_family="Consolas")
            )

    for i in range(len(dataNews['noticias'])):
        noticia = dataNews['noticias'][i]
        lv.controls.append( getNoticia(i, noticia) )

    page.add(lv, 
             botoes
            )

    page.update()


ft.app(
    main,
    assets_dir="assets"
)
