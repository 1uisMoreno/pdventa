from tkinter import SEL
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from sqlquerys import QuerisSQLite
from login.login import LoginWindow
from ventas.ventas import VentasWindow
from inventario.inventario import  InventarioWindow
from usuarios.usuarios import UsuariosWindow
from reportes.reportes import ReportesWindow
from kivy.core.window import Window


class MainWindow(BoxLayout):
    QuerisSQLite.crearTablas()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inventario=InventarioWindow()
        self.ventas=VentasWindow(self.inventario.actualizarInventario)
        self.login=LoginWindow(self.ventas.guardarUsuario)
        self.usuarios=UsuariosWindow()
        self.reportes=ReportesWindow()
        self.ids.scrn_login.add_widget(self.login)
        self.ids.scrn_ventas.add_widget(self.ventas)
        self.ids.scrn_inventario.add_widget(self.inventario)
        self.ids.scrn_usuarios.add_widget(self.usuarios)
        self.ids.scrn_reportes.add_widget(self.reportes)
        Window.bind(on_key_down=self._on_keyboard_down)
        self.login.ids.username.focus=True

    def select_node(self, node):
        node.background_color = (1, 0, 0, 1)
        return MainWindow.select_node(node)

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if(text == ' '):  
            print("Hola")
            print(keycode)
        if(text == 'e'):
            print("Mundo")
        if(text == 'ě'):
            print("Hola mundo f2")
            print(keycode)
            # Bucar por codigo
            self.ventas.ids.buscarCodigo.focus = True
        if(text == 'Ĝ'):
            print("Hola mundo f3")
            print(keycode)
            # Bucar por nombre
            self.ventas.ids.buscarNombre.focus = True
        if(text == 'ĝ'):
            print("Hola mundo f4")
        if(text == 'Ğ'):
            print("Hola mundo f5")
            print(keycode)
        if(text == 'ğ'):
            print("Hola mundo f6")
            print(keycode)
        if(text == 'Ġ'):
            print("Hola mundo f7")
            print(keycode)
        if(text == 'ġ'):
            print("Hola mundo f8")
            print(keycode)
        if(text == 'Ģ'):
            print("Hola mundo f9")
            print(keycode)
            # Borrar articulo
        if(text == 'ģ'):
            print("Hola mundo f10")
            print(keycode)
            # Cambiar cantidad
        if(text == 'Ĥ'):
            print("Hola mundo f11")
            print(keycode)
            self.ventas.pagar()
            # Pagar
        if(text == 'ĥ'):
            print("Hola mundo f12")
            print(keycode)
            # Nueva compra

        

class MainApp(App):
    def build(self):
        return MainWindow()


if __name__ == '__main__':
    MainApp().run() 




# ........._____.............me gusta 
# .......／＞　 フ ...........respirar
# .......|  -  -l ...........y el
# ......／`ミ＿xノ ...........pan 
# ...../　　　 　 | ..........con 
# ...../　 ヽ　　 ﾉ ..........jabón 
# .....│　  |　|　| ..........jamon* 
# .／￣|　　 |　|　| ..........viva 
# .| (￣ヽ＿_ヽ_)__) .........el
# .＼二つ-....................perico 
# ..................................