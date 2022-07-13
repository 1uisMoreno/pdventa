from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from sqlquerys import QuerisSQLite
from kivy.core.window import Window
Builder.load_file('login/login.kv')



class LoginWindow(BoxLayout):
    def __init__(self, apuntadorGuardarUsuario, **kwargs):
        super().__init__(**kwargs)
        self.guardarUsuario=apuntadorGuardarUsuario
 
    def validarUsuario(self, username, password):
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        queryUsuarios = "SELECT * from usuarios"
        usuarios = QuerisSQLite.lecturaQuery(conexion,queryUsuarios)
        if username=='' or password=='':
            self.ids.notificacion_login.text= "Rellena todos los datos"
        else:
            usuario = {}
            for user in usuarios:
                if user[1]==username:
                    usuario['idUsuario']=user[0]
                    usuario['password']=user[2]
                    usuario['username']=user[1]
                    usuario['nombre']=user[3]
                    usuario['telefono']=user[4]
                    usuario['tipo']=user[5]
                    break
            if usuario:
                if usuario['password']==password:
                    self.ids.username.text = ''
                    self.ids.password.text = ''
                    self.ids.notificacion_login.text= ''
                    self.parent.parent.current='scrn_ventas'
                    self.guardarUsuario(usuario)
                else:
                    self.ids.notificacion_login.text= "Contraseña incorrecta"
            else:
                self.ids.notificacion_login.text= "Usuario no encontrado"

    def inicioDirecto(self):
        self.parent.parent.current='scrn_ventas'
        
class LoginApp(App):
    def build(self):
        return LoginWindow()


if __name__ == '__main__':
    LoginApp().run()    