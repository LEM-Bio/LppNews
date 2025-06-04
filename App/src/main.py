import flet as ft
import json
from copy import deepcopy
from flet_toast import flet_toast
import os
import uploadImgur as uploadImgur
import git
import shutil
import config as config
import pynpm as npm
import paramiko
from connection import MySFTPClient
import noticias as nt
import publicacoes as publi
import equipamentos as eqp
import coordenadores as coord
import docentes as doc
import equipe as tec
import estudantes as est
import comite as com

output = os.getcwd()
paginaPath = os.path.join(f'{output}', 'LembioWebsite')
if os.path.isdir(paginaPath):
    shutil.rmtree(paginaPath)

git.Git(output).clone(f'https://{config.secret_token}@github.com/LEM-Bio/LembioWebsite.git', "--branch=main")

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
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.update()

    lv = nt.Noticia(page, dataNews, file_picker)
    pb = publi.Publicacao(page, dataNews, file_picker)
    equip = eqp.Equipamento(page, dataNews, file_picker)
    crdn = coord.Coordenador(page, dataNews, file_picker)
    docnt = doc.Docente(page, dataNews, file_picker)
    eqpTec = tec.Equipe(page, dataNews, file_picker)
    estud = est.Estudante(page, dataNews, file_picker)
    cmt = com.Comite(page, dataNews, file_picker)
    
    botoes = ft.ResponsiveRow()
    botoesPB = ft.ResponsiveRow()
    botoesEqp = ft.ResponsiveRow()
    botoesEquipe = ft.ResponsiveRow()
    
    #region Exit PopUp

    #FECHAR JSON ANTES DE FECHAR APP
    def handle_window_event(e):
        if e.data == "close" and sendingContent.open == False:
            confirm_dialog.open = True
            page.update()

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

    #endregion

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
            flet_toast.error(
                page=page,
                message="Erro ao conectar no github",
                position="top_right",
                duration=3
            )
        
        if closeDiag:
            page.close(confirmSave_dialog)
        lv.newsReset()
        pb.pbsReset()

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
        global dataNews
        dataNews = {}
        dataNews = deepcopy(dataNewsOriginal)
        
        lv.dataNews = dataNews
        pb.dataNews = dataNews
        
        lv.newsReset()
        pb.pbsReset()
        
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
    
    #region Send Content
    sendingContent = ft.AlertDialog(
        modal=True,
        title=ft.Text("Carregando conteúdo..."),
        content=ft.Container(height = 50, alignment=ft.Alignment(0,0.5), content=ft.ProgressRing(width=30, height=30, stroke_width = 3))
    )

    def trySend(e):
        user = e.control.parent.content.controls[0].value
        password = e.control.parent.content.controls[1].value
        saveYes(e, False)

        insertLogin_dialog.open = False
        sendingContent.open = True
        page.update()

        print(f'{paginaPath}{os.sep}package.json')
        pkg = npm.NPMPackage(f'{paginaPath}{os.sep}package.json')
        pkg.install()
        pkg.run_script('build', '--report')

        remote_path = "/usr/share/nginx/html"

        transport = paramiko.Transport(('172.22.161.213', 22))
        transport.connect(username=user, password=password)
        sftp = MySFTPClient.from_transport(transport)
        sftp.put_dir(os.path.join(f"{paginaPath}", "build"), remote_path)
        sftp.close()

        sendingContent.open = False
        page.update()
        

    def closeLogin(e):
        page.close(insertLogin_dialog)

    insertLogin_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Text("Insira seus dados do servidor"),
            ft.IconButton(icon=ft.Icons.CLOSE, on_click=closeLogin)
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
        insertLogin_dialog.open = True
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
                        on_click=lv.addNot
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
                        on_click=pb.addPub
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
                        on_click=equip.addEquip
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
        if equipDrop.value == "Coordenador": crdn.addCoord(e)
        elif equipDrop.value == "Docente": docnt.addCoord(e)
        elif equipDrop.value == "Tecnico": eqpTec.addCoord(e)
        elif equipDrop.value == "Estudante": estud.addCoord(e)
        elif equipDrop.value == "Usuario": cmt.addCoord(e)

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
        lv.controls.append( lv.getNoticia(noticia) )

    for i in range(len(dataNews['publicados'])):
        publicacao = dataNews['publicados'][i]
        pb.controls.append( pb.getPubli(publicacao) )

    for i in range(len(dataNews['equipamentos'])):
        equipamento = dataNews['equipamentos'][i]
        equip.controls.append( equip.getEquip(equipamento) )

    for i in range(len(dataNews['coordenadores'])):
        coordenador = dataNews['coordenadores'][i]
        crdn.controls.append( crdn.getCoord(coordenador) )

    for i in range(len(dataNews['docentes'])):
        docente = dataNews['docentes'][i]
        docnt.controls.append( docnt.getCoord(docente) )

    for i in range(len(dataNews['eqTecnica'])):
        tecnico = dataNews['eqTecnica'][i]
        eqpTec.controls.append( eqpTec.getCoord(tecnico) )

    for i in range(len(dataNews['estudantes'])):
        estudante = dataNews['estudantes'][i]
        estud.controls.append( estud.getCoord(estudante) )

    for i in range(len(dataNews['comite'])):
        usuario = dataNews['comite'][i]
        cmt.controls.append( cmt.getCoord(usuario) )

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
        ],
        expand=1,
    )
    
    page.add(tabs, confirm_dialog, confirmSave_dialog, insertLogin_dialog, confirmDiscard_dialog, sendingContent)

    page.update()


ft.app(
    main,
    assets_dir="assets"
)
