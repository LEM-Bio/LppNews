import abc
import flet as ft
from utils.toast import *
import utils.uploadImgur as uploadImgur

class WebList(abc.ABC, ft.ReorderableListView):
    def __init__(self, page: ft.Page, data={}, filepicker=ft.FilePicker(), name="", jsonSkeleton = {}):
        super().__init__(
            expand=1,
            padding=20,
            auto_scroll=False,
            on_reorder=lambda e: self.handle_reorder(e)
        )

        self.page: ft.Page = page

        self.name = name
        self.data = data
        self.filepicker = filepicker
        self.jsonSkeleton = jsonSkeleton
        self.toast_manager = Toaster(page, expand=False, position=ToastPosition.TOP_RIGHT)

        self.page.update()
        
    @abc.abstractmethod
    def getContent(self, content):
        raise NotImplementedError

    def componentReset(self):
        self.controls.clear()
        for i in range(len(self.data[self.name])):
            content = self.data[self.name][i]
            self.controls.append( self.getContent(content) )

        self.page.update()

    def addContent(self, e):
        newContent = self.jsonSkeleton

        self.data[self.name].insert(0, newContent)
        self.componentReset()

        self.toast_manager.show_toast(
            toast_type=ToastType.SUCCESS,
            text=f"Novo item adicionado"
        )

    def changeData(self, e, column, imageCol=''):
        if imageCol == '':
            index = self.controls.index(e.control.parent.parent.parent.parent.parent)
        else:
            index = self.controls.index(e.control.parent.parent.parent.parent)

        if len(self.controls) > index:
            dataToChange = str(e).split("data='")[1][0:-2]
            if imageCol == '':
                self.data[self.name][index][column] = dataToChange
                return
                
            self.data[self.name][index][column][imageCol] = dataToChange

    def removeContent(self, e):
        content = e.control.parent.parent
        index = self.controls.index(content)
        self.controls.remove(content)
        self.data[self.name].pop(index)

        self.componentReset()
        self.toast_manager.show_toast(
            toast_type=ToastType.SUCCESS,
            text=f"Item removido"
        )

    def handle_reorder(self, e: ft.OnReorderEvent):
        self.data[self.name][e.old_index], self.data[self.name][e.new_index] = self.data[self.name][e.new_index], self.data[self.name][e.old_index]
        self.componentReset()
        self.page.update()


    def on_dialog_result(self, e: ft.FilePickerResultEvent):
        path = e.files[0].path
        imgurUrl = uploadImgur.uploadImage(path)
        e.control.parent.parent.controls[0].value = imgurUrl
        
        imageTextField.value = imgurUrl
        index = self.controls.index(imageTextField.parent.parent.parent.parent)

        if len(self.controls) > index:
            self.data[self.name][index]['image']['url'] = imgurUrl
        self.componentReset()

    def pickFiles(self, e):
        global imageTextField
        imageTextField = e.control.parent.controls[0]
        
        self.filepicker.on_result = self.on_dialog_result
        self.filepicker.pick_files(allow_multiple=False)