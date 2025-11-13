import flet as ft
import sys
import json
import pandas as pd
from copy import deepcopy
from utils.toast import *
import os
import utils.uploadImgur as uploadImgur
import git
import shutil
import config as config
import pynpm as npm
import paramiko
from setup.connection import MySFTPClient
from webComponents import *
from webComponents.membersComponents import *
import setup.databaseConn as db
from setup.login import LogInfo as login

output = os.getcwd()
paginaPath = os.path.join(f'{output}', 'LembioWebsite')
if os.path.isdir(paginaPath):
    shutil.rmtree(paginaPath)

git.Git(output).clone(f'https://{config.secret_token}@github.com/LEM-Bio/LembioWebsite.git', "--branch=main")

repo = git.Repo(paginaPath)
repo.git.init()
repo.config_writer().set_value("user", "name", "pedroand6").release()
repo.config_writer().set_value("user", "email", "redbrickcar2@gmail.com").release()
repo.git.remote("set-url", "origin", f"https://{config.secret_token}@github.com/LEM-Bio/LembioWebsite.git")

currentAuth = login("", "", "")

#Carrega os dados
jsonPath = os.path.join(f'{output}', 'LembioWebsite', 'src', 'data', 'components-mock.json')

fNews = open(jsonPath, "r")
fNews2 = open(jsonPath, "r")

global dataNewsOriginal
global dataNews
dataNewsOriginal = json.load(fNews)
fNews.close()

dataNews = json.load(fNews2)
fNews2.close()

global database
global conn
conn = db.ConnectDB("", "")
database = pd.DataFrame([]) #Mock database

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.title = "Aplicativo para atualização do Website LEMbio"
    page.window.min_height = 300
    page.window.min_width = 450

    def route_change(route):
        if page.route == "/":
            page.views.clear()
            page.views.append(logApp(page))
        elif page.route == "/main":
            page.views.clear()
            page.views.append(mainApp(page))
        page.update()

    page.on_route_change = route_change
    page.go("/")

def logApp(page: ft.Page):
    toast_manager = Toaster(page, expand=False, position=ToastPosition.TOP_RIGHT)

    def LogIn(e):
        hostField = e.control.parent.content.controls[0]
        userField = e.control.parent.content.controls[1]
        passField = e.control.parent.content.controls[2]

        currentAuth.host = hostField.value
        currentAuth.user = userField.value
        currentAuth.password = passField.value
        hostField.read_only = True
        userField.read_only = True
        passField.read_only = True
        page.update()
        if currentAuth.checkValidation(): 
            currentAuth.logged = True
            #Connect to Database
            global conn
            conn = db.ConnectDB(user=currentAuth.user, password=currentAuth.password)
            global database
            database = conn.GetAllData()
            global originalDatabase
            originalDatabase = {}
            originalDatabase = deepcopy(database)
            global databaseLen
            databaseLen = database.shape[0]
            page.go("/main")
        else:
            toast_manager.show_toast(
                toast_type=ToastType.ERROR,
                text="Usuario ou senha incorretos",
            ),

            hostField.read_only = False
            userField.read_only = False
            passField.read_only = False
            page.update()

    insertLogin_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Text("Insira seus dados do servidor"),
            ]),
        content=ft.Column([
            ft.TextField(label="Host (IP do servidor)", read_only=False, value="172.22.161.213"), #TODO: Change to a list of ips checking the website connection in the network
            ft.TextField(label="Usuario", read_only=False),
            ft.TextField(label="Senha", password=True, can_reveal_password=True, read_only=False)
        ], height=200),
        actions=[
            ft.ElevatedButton("Enviar", on_click=LogIn),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    insertLogin_dialog.open = True #Ask login when start

    return ft.View(
        "/",
        controls=[
            insertLogin_dialog
        ],
    )

def mainApp(page: ft.Page):
    toast_manager = Toaster(page, expand=False, position=ToastPosition.TOP_RIGHT)

    #region Send Content
    sendingContent = ft.AlertDialog(
        modal=True,
        title=ft.Text("Carregando conteúdo..."),
        content=ft.Container(height = 50, alignment=ft.Alignment(0,0.5), content=ft.ProgressRing(width=30, height=30, stroke_width = 3))
    )
    
    def trySend(e):
        page.window.prevent_close = True
        sendingContent.open = True
        sendingContent.modal = True
        saveYes(e, False)
        page.update()

        pkg = npm.NPMPackage(f'{paginaPath}{os.sep}package.json')
        pkg.install()
        pkg.run_script('build', '--report')

        remote_path = "/usr/share/nginx/html"

        transport = paramiko.Transport((currentAuth.host, 22))
        transport.connect(username=currentAuth.user, password=currentAuth.password)
        sftp = MySFTPClient.from_transport(transport)
        sftp.put_dir(os.path.join(f"{paginaPath}", "build"), remote_path)
        sftp.close()

        try:
            global databaseLen
            database = deepcopy(art.data)
            newDataLen = database.shape[0]

            print(database)

            print(f"antigo: {databaseLen}")
            print(f"novo: {newDataLen}")

            count = 0
            for index, row in database.iterrows():
                sql = f'UPDATE pubsLEMBio SET id = {count+1}, ano = {row["ano"]}, texto = "{row["texto"]}", link = "{row["link"]}" where id = {count+1}'
                conn.ExcuteQuery(sql)
                count += 1
            
            if newDataLen > databaseLen:
                for index, row in database.iloc[databaseLen: newDataLen].iterrows():
                    sql = f'INSERT INTO pubsLEMBio SET id = {row["id"]}, ano = {row["ano"]}, texto = "{row["texto"]}", link = "{row["link"]}"'
                    conn.ExcuteQuery(sql)
            elif newDataLen < databaseLen:
                for i in range(databaseLen - newDataLen):
                    print(databaseLen + i)
                    sql = f'DELETE FROM pubsLEMBio WHERE id = {databaseLen + i}'
                    conn.ExcuteQuery(sql)
        except Exception as err:
            print(err)

        sendingContent.open = False
        page.window.prevent_close = False
        page.update()

    def sendNo(e):
        page.close(confirmSend_dialog)

    confirmSend_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirme"),
        content=ft.Text("Voce realmente quer enviar os dados?"),
        actions=[
            ft.ElevatedButton("Sim", on_click=trySend),
            ft.OutlinedButton("Nao", on_click=sendNo),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def sendData(e):
        confirmSend_dialog.open = True
        e.page.open(confirmSend_dialog)
        e.page.update()
    
    #endregion

    #region Exit PopUp

    #FECHAR JSON ANTES DE FECHAR APP
    def handle_window_event(e):
        if e.data == "close" and sendingContent.open == False:
            confirm_dialog.open = True
            page.update()
        elif e.data == "close" and sendingContent.open == True:
            page.update()
        elif e.data == "close":
            handle_yes(e)

    page.window.prevent_close = True
    page.window.on_event = handle_window_event

    def handle_yes(e):
        wNews = open(jsonPath, "w")

        json.dump(dataNewsOriginal, wNews, indent=2)
        wNews.close()
        conn.CloseConnection()
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

    #endregion

    global dataNewsOriginal
    global dataNews

    #DEFINIR O QUE APARECE NA TELA
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    lv = noticias.Noticia(page, dataNews, file_picker)
    pb = publicacoes.Publicacao(page, dataNews, file_picker)
    equip = equipamentos.Equipamento(page, dataNews, file_picker)
    crdn = coordenadores.Coordenador(page, dataNews, file_picker)
    docnt = docentes.Docente(page, dataNews, file_picker)
    eqpTec = equipe.Equipe(page, dataNews, file_picker)
    estud = estudantes.Estudante(page, dataNews, file_picker)
    cmt = comite.Comite(page, dataNews, file_picker)
    art = artigos.Artigo(page, database)

    components = [lv, pb, equip, crdn, docnt, eqpTec, estud, cmt, art]
    
    botoes = ft.ResponsiveRow()
    botoesPB = ft.ResponsiveRow()
    botoesEqp = ft.ResponsiveRow()
    botoesEquipe = ft.ResponsiveRow()
    botoesArt = ft.ResponsiveRow()

    #region Save PopUp

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
            toast_manager.show_toast(
                toast_type=ToastType.WARNING,
                text="Erro ao enviar ao github",
            ),
        
        if closeDiag:
            page.close(confirmSave_dialog)

        for component in components:
            component.componentReset()

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
        confirmSave_dialog.open = True
        page.update()

    #endregion

    #region Discard Popup
    def discardYes(e):
        database = {}
        database = deepcopy(originalDatabase)

        global dataNews
        dataNews = {}
        dataNews = deepcopy(dataNewsOriginal)
        
        for comp in components:
            comp.data = dataNews

            if(comp == art):
                comp.data = database
                comp.states = [False for i in range(len(comp.data))]
            else:
                comp.states = [False for i in range(len(comp.data[comp.name]))]
    
            comp.componentReset() #FIXME

        art.data = database
        
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
        confirmDiscard_dialog.open = True
        page.update()

    #endregion

    #region Definindo os botoes de salvamento, descarte, adiçao de noticias e envio ao servidor
    botoes.controls.append(
        ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Adicionar noticia",
                        on_click=lv.addContent
                    ),
                    ft.ElevatedButton("Salvar", on_click=saveData, bgcolor="green", color="white"),
                    ft.ElevatedButton("Descartar", on_click=discardData, bgcolor="red", color="white"),
                    ft.IconButton(
                        icon=ft.Icons.SEND,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Enviar dados salvos ao servidor",
                        on_click=sendData,
                    )
                ],
                alignment="CENTER",
            )
    )
    
    botoesPB.controls.append(
        ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Adicionar publicação",
                        on_click=pb.addContent
                    ),
                    ft.ElevatedButton("Salvar", on_click=saveData, bgcolor="green", color="white"),
                    ft.ElevatedButton("Descartar", on_click=discardData, bgcolor="red", color="white"),
                    ft.IconButton(
                        icon=ft.Icons.SEND,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Enviar dados salvos ao servidor",
                        on_click=sendData,
                    )
                ],
                alignment="CENTER",
            )
    )

    botoesEqp.controls.append(
        ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Adicionar equipamento",
                        on_click=equip.addContent
                    ),
                    ft.ElevatedButton("Salvar", on_click=saveData, bgcolor="green", color="white"),
                    ft.ElevatedButton("Descartar", on_click=discardData, bgcolor="red", color="white"),
                    ft.IconButton(
                        icon=ft.Icons.SEND,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Enviar dados salvos ao servidor",
                        on_click=sendData,
                    )
                ],
                alignment="CENTER",
                visible=True
            )
    )

    botoesArt.controls.append(
        ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Adicionar artigo",
                        on_click=art.addContent
                    ),
                    ft.ElevatedButton("Salvar", on_click=saveData, bgcolor="green", color="white"),
                    ft.ElevatedButton("Descartar", on_click=discardData, bgcolor="red", color="white"),
                    ft.IconButton(
                        icon=ft.Icons.SEND,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Enviar dados salvos ao servidor",
                        on_click=sendData,
                    )
                ],
                alignment="CENTER",
            )
    )

    equipDrop = ft.Dropdown(
                        leading_icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                        label="Adicionar",
                        tooltip="Adicionar na equipe",
                        value="Coordenador",
                        options=[
                            ft.DropdownOption("Coordenador"),
                            ft.DropdownOption("Docente"),
                            ft.DropdownOption("Tecnico"),
                            ft.DropdownOption("Estudante"),
                            ft.DropdownOption("Usuario")
                        ]
                    )
    
    def addEquipe(e):
        if equipDrop.value == "Coordenador": crdn.addContent(e)
        elif equipDrop.value == "Docente": docnt.addContent(e)
        elif equipDrop.value == "Tecnico": eqpTec.addContent(e)
        elif equipDrop.value == "Estudante": estud.addContent(e)
        elif equipDrop.value == "Usuario": cmt.addContent(e)

    botoesEquipe.controls.append(
        ft.Row(
                [
                    equipDrop,
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Adicionar a equipe",
                        on_click=addEquipe
                    ),
                    ft.ElevatedButton("Salvar", on_click=saveData, bgcolor="green", color="white"),
                    ft.ElevatedButton("Descartar", on_click=discardData, bgcolor="red", color="white"),
                    ft.IconButton(
                        icon=ft.Icons.SEND,
                        icon_color="blue400",
                        icon_size=40,
                        tooltip="Enviar dados salvos ao servidor",
                        on_click=sendData,
                    )
                ],
                alignment="CENTER",
            )
    )

    #endregion

    for i in range(len(dataNews['noticias'])):
        noticia = dataNews['noticias'][i]
        lv.controls.append( lv.getContent(noticia) )

    for i in range(len(dataNews['publicados'])):
        publicacao = dataNews['publicados'][i]
        pb.controls.append( pb.getContent(publicacao) )

    for i in range(len(dataNews['equipamentos'])):
        equipamento = dataNews['equipamentos'][i]
        equip.controls.append( equip.getContent(equipamento) )

    for i in range(len(dataNews['coordenadores'])):
        coordenador = dataNews['coordenadores'][i]
        crdn.controls.append( crdn.getContent(coordenador) )

    for i in range(len(dataNews['docentes'])):
        docente = dataNews['docentes'][i]
        docnt.controls.append( docnt.getContent(docente) )

    for i in range(len(dataNews['eqTecnica'])):
        tecnico = dataNews['eqTecnica'][i]
        eqpTec.controls.append( eqpTec.getContent(tecnico) )

    for i in range(len(dataNews['estudantes'])):
        estudante = dataNews['estudantes'][i]
        estud.controls.append( estud.getContent(estudante) )

    for i in range(len(dataNews['comite'])):
        usuario = dataNews['comite'][i]
        cmt.controls.append( cmt.getContent(usuario) )

    for i in range(len(database)):
        artigo = database.iloc[i].to_dict()
        art.controls.append( art.getContent(artigo) )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Notícias",
                content=ft.Column([
                    lv,
                    botoes
                ])
            ),
            ft.Tab(
                text="Publicações",
                content=ft.Column([
                    pb,
                    botoesPB
                ])
            ),
            ft.Tab(
                text="Equipamentos",
                content=ft.Column([
                    equip,
                    botoesEqp
                ])
            ),
            ft.Tab(
                text="Equipe",
                content=ft.Column([
                    ft.Container(height=10),
                    ft.Text(
                        "Coordenadores",
                        size=24,
                        font_family="Consolas",
                    ),
                    ft.Divider(),
                    crdn,
                    ft.Text(
                        "Docentes",
                        size=24,
                        font_family="Consolas"
                    ),
                    ft.Divider(),
                    docnt,
                    ft.Text(
                        "Equipe Tecnica",
                        size=24,
                        font_family="Consolas"
                    ),
                    ft.Divider(),
                    eqpTec,
                    ft.Text(
                        "Estudantes",
                        size=24,
                        font_family="Consolas"
                    ),
                    ft.Divider(),
                    estud,
                    ft.Text(
                        "Comite de Usuarios",
                        size=24,
                        font_family="Consolas"
                    ),
                    ft.Divider(),
                    cmt,
                    botoesEquipe
                ], scroll=ft.ScrollMode.AUTO)
            ),
            ft.Tab(
                text="Artigos",
                content=ft.Column([
                    art,
                    botoesArt
                ])
            ),
        ],
        expand=1,
    )
    
    return ft.View(
        "/main",
        controls=[
            tabs, confirm_dialog, confirmSave_dialog, confirmDiscard_dialog, sendingContent
        ],
    )


ft.app(
    main,
    assets_dir="assets"
)
