
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder
from sqlquerys import QuerisSQLite

Builder.load_file('usuarios/usuarios.kv')
class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)

class SelectableUsuarioLabel(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids['_idUsuario'].text = str(data["id_usuario"])
        self.ids['_username'].text = data["username"]
        self.ids['_nombre'].text = data["nombre"]
        self.ids['_telefono'].text = str(data["telefono"])
        self.ids['_tipo'].text = data["tipo"].capitalize()
        return super(SelectableUsuarioLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableUsuarioLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.data[index]['seleccionado']=True
        else:
            rv.data[index]['seleccionado']=False

class RV_usuarios(RecycleView):
    def __init__(self, **kwargs):
        super(RV_usuarios, self).__init__(**kwargs)
        self.data = []

    def agregarDatos(self, datos):
        for dato in datos:
            dato['seleccionado']=False
            self.data.append(dato)
        self.refresh_from_data()

    def usuarioSeleccionado(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
                break
        return indice



class VentanaUsuarios(Popup):
    def __init__(self, apuntadorAgregar_Modificar_Usuario, **kwargs):
        super(VentanaUsuarios, self).__init__(**kwargs)
        self.agregar_Modificar_Usuario = apuntadorAgregar_Modificar_Usuario

    def mostrarContraseña(self, estado):
        if estado=='normal':
            self.ids.passwordVentanaUsuarios.password=True
            self.ids.imagePassword.source='img/eye-slash-regular.png'
        elif estado=='down':
            self.ids.passwordVentanaUsuarios.password=False
            self.ids.imagePassword.source='img/eye-regular.png'

    def abrir(self,agregar,modificar, Usuario=None):
        if agregar==True and modificar==False:
            self.ids.notificacionVentanaUsuarios.text = ''
            self.ids.botonAgregarUsuario.text='Agregar'
        elif modificar==True and agregar==False:
            self.ids.notificacionVentanaUsuarios.text = ''
            self.ids.botonAgregarUsuario.text='Modificar'
            self.ids.idUsuarioVentanaUsuarios.disabled=True
            self.ids.idUsuarioVentanaUsuarios.text=str(Usuario["id_usuario"])
            self.ids.nombreVentanaUsuarios.text = str(Usuario["nombre"])
            self.ids.usernameVentanaUsuarios.text = str(Usuario["username"])
            self.ids.celularVentanaUsuarios.text = str(Usuario["telefono"])
            self.ids.passwordVentanaUsuarios.text = str(Usuario["password"])
            if Usuario["tipo"]==self.ids.labelAdminVentanaUsuarios.text:
                self.ids.adminValueCheckbox.active=True
            elif Usuario["tipo"]==self.ids.labelEmpleadoVentanaUsuarios.text:
                self.ids.empleadoValueCheckbox.active=True
        self.open()
    
    def validar(self, id_usuario,nombre,username,celular,password,mostrarContra,adminValue,empleadoValue):
        alerta = 'Falta: '
        alerta2 = ''
        datosValidados = {}
        if not id_usuario:
            alerta+="ID. "
            datosValidados["id_usuario"]=False
        else:
            try:
                int(id_usuario)
                datosValidados["id_usuario"]=id_usuario
            except:
                alerta2+='ID no valido'
                datosValidados["id_usuario"]=False   
        if not nombre:
            alerta+="Nombre. "
            datosValidados["nombre"]=False
        else:
            datosValidados["nombre"]=nombre

        if not username:
            alerta+='Username. '
            datosValidados["username"]=False
        else:
            datosValidados["username"]=username

        if not celular:
            alerta+='Telefono. '
            datosValidados["telefono"]=False
        else:
            datosValidados["telefono"]=celular
        if not password:
            alerta+='Contraseña. '
            datosValidados["password"]=False
        else:
            datosValidados["password"]=password
        if adminValue==False and empleadoValue==False:
            alerta+='Tipo. '
            datosValidados["tipo"]=False
        else:
            if adminValue==True and empleadoValue==False:
                datosValidados["tipo"]='Admin'
            elif adminValue==False and empleadoValue==True:
                datosValidados["tipo"]='Empleado'
        valores = list(datosValidados.values())
        if False in valores:
            self.ids.notificacionVentanaUsuarios.text = alerta+alerta2
        else:
            self.ids.notificacionVentanaUsuarios.text = 'Validado'
            datosValidados["id_usuario"]=int(datosValidados["id_usuario"])
            self.agregar_Modificar_Usuario(True, datosValidados)
            self.dismiss()

class UsuariosWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.cargarUsuariosRV,1)

    def cargarUsuariosRV(self, *args):
        _data = []
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        queryUsuarios = """SELECT * from usuarios"""
        usuarios = QuerisSQLite.lecturaQuery(conexion,queryUsuarios)
        if usuarios:
            for usuario in usuarios:
                _data.append({"id_usuario":usuario[0],"username":usuario[1],"password":usuario[2],"nombre":usuario[3],"telefono":usuario[4],"tipo":usuario[5]})
            self.ids.rv_usuarios.agregarDatos(_data)

    def agregarUsuario(self, agregar=False, datosValidados=None):
        if agregar==True:
            usuarioTuple=(datosValidados["id_usuario"],datosValidados["username"],datosValidados["password"],datosValidados["nombre"],datosValidados["telefono"],datosValidados["tipo"])
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            crearUsuarioQuery="""
            INSERT INTO
                usuarios (idUsuario,username,password,nombre,telefono,tipo)
            VALUES
                (?,?,?,?,?,?);
            """
            QuerisSQLite.ejecutarQuery(conexion,crearUsuarioQuery,usuarioTuple)
            print(datosValidados)
            self.ids.rv_usuarios.data.append(datosValidados)
            self.ids.rv_usuarios.refresh_from_data()
        else:
            ventanaAgregar=VentanaUsuarios(self.agregarUsuario)
            ventanaAgregar.abrir(True,False)

    def modificarUsuario(self, modificar=False, datosValidados=None):
        indice=self.ids.rv_usuarios.usuarioSeleccionado()
        if modificar==True:
            productoTuple=(datosValidados["username"],datosValidados["password"],datosValidados["nombre"],datosValidados["telefono"],datosValidados["tipo"],datosValidados["id_usuario"])
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            actualizarProductoQuery="""
            UPDATE
                usuarios
            SET
                username=?, password=?, nombre=?, telefono=?, tipo=?
            WHERE
                idUsuario=? 
            """
            QuerisSQLite.ejecutarQuery(conexion,actualizarProductoQuery,productoTuple)
            self.ids.rv_usuarios.data[indice]["username"]=datosValidados["username"]
            self.ids.rv_usuarios.data[indice]["password"]=datosValidados["password"]
            self.ids.rv_usuarios.data[indice]["nombre"]=datosValidados["nombre"]
            self.ids.rv_usuarios.data[indice]["telefono"]=datosValidados["telefono"]
            self.ids.rv_usuarios.data[indice]["tipo"]=datosValidados["tipo"]
            print(datosValidados)
            self.ids.rv_usuarios.refresh_from_data()
        else:
            if indice>=0:
                usuario_a_modificar=self.ids.rv_usuarios.data[indice]
                ventanaAgregar=VentanaUsuarios(self.modificarUsuario)
                ventanaAgregar.abrir(False,True,usuario_a_modificar)

    def eliminarUsuario(self):
        indice=self.ids.rv_usuarios.usuarioSeleccionado()
        if indice>=0:
            usuarioEliminado=(self.ids.rv_usuarios.data[indice]["id_usuario"],)
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            eliminarUsuarioQuery="DELETE from usuarios WHERE idUsuario=?"
            QuerisSQLite.ejecutarQuery(conexion,eliminarUsuarioQuery,usuarioEliminado)
            self.ids.rv_usuarios.data.pop(indice)
            self.ids.rv_usuarios.refresh_from_data()

    def inventario(self):
        self.parent.parent.current='scrn_inventario'

    def reportes(self):
        self.parent.parent.current='scrn_reportes'
        
    def ventas(self):
        self.parent.parent.current='scrn_ventas'

    def cerrarSesion(self):
        self.parent.parent.current='scrn_login'
        
class UsuariosApp(App):
    def build(self):
        return UsuariosWindow()


if __name__ == '__main__':
    UsuariosApp().run() 