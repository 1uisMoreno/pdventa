from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview import RecycleView
from kivy.clock import Clock
from kivy.uix.popup import Popup
from sqlquerys import QuerisSQLite
from kivy.lang import Builder
Builder.load_file('inventario/inventario.kv')

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)

# ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# RV Categorias y ventana agregar / modificar categorias

class SelectableCategoriasLabel(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids['_idCategoria'].text = str(data["idCategoria"])
        self.ids['_Categoria'].text = data["categoria"]
        return super(SelectableCategoriasLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableCategoriasLabel, self).on_touch_down(touch):
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

class RV_categorias(RecycleView):
    def __init__(self, **kwargs):
        super(RV_categorias, self).__init__(**kwargs)
        self.data = []

    def agregarDatos(self, datos):
        for dato in datos:
            dato['seleccionado']=False
            self.data.append(dato)
        self.refresh_from_data()

    def categoriaSeleccionada(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
                break
        return indice



class VentanaCategorias(Popup):
    def __init__(self, apuntador_Agregar_Modificar_Categoria,Accion,**kwargs):
        super(VentanaCategorias, self).__init__(**kwargs)
        self.agregar_Modificar_Categoria= apuntador_Agregar_Modificar_Categoria
        self.accion=Accion

    def abrir(self,agregar,modificar, categoria=None):
        if agregar==True and modificar==False:
            self.ids.notificacionVentanaCategorias.text = ''
            self.ids.boton_Agregar_Modificar_Categoria.text='Agregar'
            self.ids.idCategoriaVentanaCategorias.disabled = False
        elif modificar==True and agregar==False:
            self.ids.notificacionVentanaCategorias.text = ''
            self.ids.boton_Agregar_Modificar_Categoria.text='Modificar'
            self.ids.idCategoriaVentanaCategorias.text = str(categoria["idCategoria"])
            self.ids.idCategoriaVentanaCategorias.disabled = True
            self.ids.categoriaVentanaCategorias.text = categoria["categoria"]
            if categoria["temporalidad"]==self.ids.label_Si_TemporalidadVentanaCategorias.text:
                self.ids.si_temporalidadValueCheckbox.active=True
            elif categoria["temporalidad"]==self.ids.label_No_TemporalidadVentanaCategorias.text:
                self.ids.no_temporalidadValueCheckbox.active=True
        self.open()
    
    def validar(self,idCateogria, categoria, si_temporalidad, no_temporalidad):
        print("Validar Categoria: ",idCateogria, categoria, si_temporalidad, no_temporalidad)
        alerta1 = 'Falta: '
        alerta2 = ''
        datosValidados = {}
        if not idCateogria:
            alerta1+='ID de Categoria. '
            datosValidados["idCategoria"]=False
        else:
            try:
                idCateogriaInt = int(idCateogria)
                datosValidados["idCategoria"]=idCateogria
            except:
                alerta2+='ID de Categoria no valido'
                datosValidados["idCategoria"]=False
        if not categoria:
            alerta1+="Categoria. "
            datosValidados["categoria"]=False
        else:
            datosValidados["categoria"]=categoria.upper()
        if si_temporalidad==False and no_temporalidad==False:
            alerta+='Temporalidad. '
            datosValidados["temporalidad"]=False
        else:
            if si_temporalidad==True and no_temporalidad==False:
                datosValidados["temporalidad"]='Si'
            elif si_temporalidad==False and no_temporalidad==True:
                datosValidados["temporalidad"]='No'
        valores = list(datosValidados.values())
        if self.accion=='Agregar':
            if False in valores:
                self.ids.notificacionVentanaCategorias.text = alerta1+alerta2
            else:
                self.ids.notificacionVentanaCategorias.text = 'Validado'
                datosValidados["idCategoria"]=int(datosValidados["idCategoria"])
                conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
                tablaCategorias="SELECT * from categorias"
                categorias=QuerisSQLite.lecturaQuery(conexion,tablaCategorias)
                existencia=False
                if categorias:
                    for cat in categorias:
                        if int(datosValidados["idCategoria"])==cat[0]:
                            existencia=True
                            break
                    if existencia==True:
                        self.ids.notificacionVentanaCategorias.text = 'ID de Categoria existente'
                    else:
                        self.agregar_Modificar_Categoria(True, datosValidados)
                    self.dismiss()
        elif self.accion=='Modificar':
            if False in valores:
                self.ids.notificacionVentanaCategorias.text = alerta1+alerta2
            else:
                self.ids.notificacionVentanaCategorias.text = 'Validado'
                datosValidados["idCategoria"]=int(datosValidados["idCategoria"])
                self.agregar_Modificar_Categoria(True, datosValidados)
                self.dismiss()


class VentanaCategoriasInventario(Popup):
    def __init__(self, **kwargs):
        super(VentanaCategoriasInventario, self).__init__(**kwargs)

    def cargarCategoriasRV(self, *args):
            _data = []
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            queryCategorias = "SELECT * from categorias"
            cateogrias = QuerisSQLite.lecturaQuery(conexion,queryCategorias)
            if cateogrias:
                for categoria in cateogrias:
                    _data.append({"idCategoria":categoria[0],"categoria":categoria[1],"temporalidad":categoria[2]})
                self.ids.rv_categorias.agregarDatos(_data)


    def agregarCategoria(self, agregar=False, datosValidados=None):
        if agregar==True:
            categoriaTuple=(datosValidados["idCategoria"],datosValidados["categoria"],datosValidados["temporalidad"])
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            crearProductoQuery="""
            INSERT INTO
                categorias (idCategoria,categoria,temporalidad)
            VALUES
                (?,?,?);
            """
            QuerisSQLite.ejecutarQuery(conexion,crearProductoQuery,categoriaTuple)
            print(datosValidados)
            self.ids.rv_categorias.data.append(datosValidados)
            self.ids.rv_categorias.refresh_from_data()
        else:
            accion='Agregar'
            ventanaAgregar=VentanaCategorias(self.agregarCategoria, accion)
            ventanaAgregar.abrir(True,False)


    def modificarCategoria(self, modificar=False, datosValidados=None):
        indice=self.ids.rv_categorias.categoriaSeleccionada()
        if modificar==True:
            categoriaTuple=(datosValidados["categoria"],datosValidados["temporalidad"],datosValidados["idCategoria"])
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            actualizarCategoriaQuery="""
            UPDATE
                categorias
            SET
                categoria=?, temporalidad=?
            WHERE
                idCategoria=? 
            """
            QuerisSQLite.ejecutarQuery(conexion,actualizarCategoriaQuery,categoriaTuple)
            self.ids.rv_categorias.data[indice]["categoria"]=datosValidados["categoria"]
            self.ids.rv_categorias.data[indice]["temporalidad"]=datosValidados["temporalidad"]
            print(datosValidados)
            self.ids.rv_categorias.refresh_from_data()
        else:
            if indice>=0:
                accion='Modificar'
                categoria_a_modificar=self.ids.rv_categorias.data[indice]
                ventanaModificar=VentanaCategorias(self.modificarCategoria, accion)
                ventanaModificar.abrir(False,True,categoria_a_modificar)

    def eliminarCategoria(self):
        indice=self.ids.rv_categorias.categoriaSeleccionada()
        if indice>=0:
            categoriaEliminada=(self.ids.rv_categorias.data[indice]["idCategoria"],)
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            eliminarCategoriaQuery="DELETE from categorias WHERE idCategoria=?"
            QuerisSQLite.ejecutarQuery(conexion,eliminarCategoriaQuery,categoriaEliminada)
            self.ids.rv_categorias.data.pop(indice)
            self.ids.rv_categorias.refresh_from_data()


# ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# RV inventario y ventana agregar / modificar

class SelectableInventarioLabel(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids['_codigo'].text = str(data["codigo"])
        self.ids['_articulo'].text = data["nombre"].capitalize()
        self.ids['_cantidad'].text = str(data["cantidad"])
        self.ids['_precio'].text = str("{:.2f}".format(data["precioPublico"]))
        self.ids['_NumDeCategoria'].text = str(data["numDeCategoria"])
        self.ids['_Categoria'].text = str(data["Categoria"])
        return super(SelectableInventarioLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableInventarioLabel, self).on_touch_down(touch):
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

class RV_inventario(RecycleView):
    def __init__(self, **kwargs):
        super(RV_inventario, self).__init__(**kwargs)
        self.data = []

    def agregarDatos(self, datos):
        for dato in datos:
            dato['seleccionado']=False
            self.data.append(dato)
        self.refresh_from_data()

    def articuloSeleccionado(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
                break
        return indice


# Ventana productos inventario

class VentanaProductosInventario(Popup):
    def __init__(self, apuntadorAgregar_Modificar_Producto, **kwargs):
        super(VentanaProductosInventario, self).__init__(**kwargs)
        self.agregar_Modificar_Producto = apuntadorAgregar_Modificar_Producto


    def abrir(self,agregar,modificar, Producto=None):
        if agregar==True and modificar==False:
            self.ids.notificacionVentanaProductos.text = ''
            self.ids.botonAgregarProducto.text='Agregar'
            self.ids.codigoVentanaProductos.disabled = False
        elif modificar==True and agregar==False:
            self.ids.notificacionVentanaProductos.text = ''
            self.ids.botonAgregarProducto.text='Modificar'
            self.ids.codigoVentanaProductos.text = str(Producto["codigo"])
            self.ids.codigoVentanaProductos.disabled = True
            self.ids.nombreVentanaProductos.text = Producto["nombre"]
            self.ids.precioVentanaProductos.text = str(Producto["precio"])
            self.ids.precioPublicoVentanaProductos.text = str(Producto["precioPublico"])
            self.ids.cantidadVentanaProductos.text = str(Producto["cantidad"])
            self.ids.numCategoriaVentanaProductos.text = str(Producto["numDeCategoria"])        
        self.open()
    
    def validar(self,codigo, nombre, precio, precioPublico, cantidad, numCategoria):
        print(codigo, nombre, precio, precioPublico, cantidad, numCategoria)
        alerta1 = 'Falta: '
        alerta2 = ''
        datosValidados = {}
        if not codigo:
            alerta1+='Codigo. '
            datosValidados["codigo"]=False
        else:
            try:
                codigoInt = int(codigo)
                datosValidados["codigo"]=codigo
            except:
                alerta2+='Codigo no valido'
                datosValidados["codigo"]=False
        if not nombre:
            alerta1+="Nombre. "
            datosValidados["nombre"]=False
        else:
            datosValidados["nombre"]=nombre
        if not precio:
            alerta1+='Precio. '
            datosValidados["precio"]=False
        else:
            try:
                precioInt = float(precio)
                datosValidados["precio"]=precio
            except:
                alerta2+='Precio no valido'
                datosValidados["precio"]=False
        if not precioPublico:
            alerta1+='Precio Publico. '
            datosValidados["precioPublico"]=False
        else:
            try:
                precioPublicoInt = float(precio)
                datosValidados["precioPublico"]=precioPublico
            except:
                alerta2+='Precio Publico no valido'
                datosValidados["precioPublico"]=False
        if not cantidad:
            alerta1+='Cantidad. '
            datosValidados["cantidad"]=False
        else:
            try:
                cantidadInt = int(cantidad)
                datosValidados["cantidad"]=cantidad
            except:
                alerta2+='Cantidad no valida'
                datosValidados["cantidad"]=False
        if not numCategoria:
            alerta1+='No. de Categoria. '
            datosValidados["numDeCategoria"]=False
        else:
            try:
                numCategoriaInt = int(numCategoria)
                datosValidados["numDeCategoria"]=numCategoria
            except:
                alerta2+='No. de Categoria No Valido'
                datosValidados["numDeCategoria"]=False
        valores = list(datosValidados.values())
        if False in valores:
            self.ids.notificacionVentanaProductos.text = alerta1+alerta2
        else:
            self.ids.notificacionVentanaProductos.text = 'Validado'
            datosValidados["codigo"]=int(datosValidados["codigo"])
            datosValidados["precio"]=float(datosValidados["precio"])
            datosValidados["precioPublico"]=float(datosValidados["precioPublico"])
            datosValidados["cantidad"]=int(datosValidados["cantidad"])
            datosValidados["numDeCategoria"]=int(datosValidados["numDeCategoria"])
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            tablaCategorias="""
            SELECT * from categorias
            """
            categorias=QuerisSQLite.lecturaQuery(conexion,tablaCategorias)
            print(categorias)
            if categorias:
                try:
                    for cat in categorias:
                        if datosValidados["numDeCategoria"]==cat[0]:
                            datosValidados["Categoria"]=cat[1]
                            self.agregar_Modificar_Producto(True, datosValidados)
                            self.dismiss()
                            break
                except:
                    self.ids.notificacionVentanaProductos.text = 'Categoria no valida'


# ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# Ventana Inventario

class InventarioWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)        
        Clock.schedule_once(self.cargarProductosRV,1)

    def cargarProductosRV(self, *args):
        _data = []
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        queryInventario = """
        SELECT * from
            (SELECT * from productos),
            (SELECT idCategoria, categoria from categorias) 
        WHERE (numCategoria = idCategoria);
        """
        inventario = QuerisSQLite.lecturaQuery(conexion,queryInventario)
        if inventario:
            for producto in inventario:
                _data.append({"codigo":producto[0],"nombre":producto[1],"precio":producto[2],"precioPublico":producto[3],"cantidad":producto[4],"numDeCategoria":producto[5],"Categoria":producto[7]})
            self.ids.rv_inventario.agregarDatos(_data)

    def agregarProducto(self, agregar=False, datosValidados=None):
        if agregar==True:
            productoTuple=(datosValidados["codigo"],datosValidados["nombre"],datosValidados["precio"],datosValidados["precioPublico"],datosValidados["cantidad"],datosValidados["numDeCategoria"])
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            crearProductoQuery="""
            INSERT INTO
                productos (codigo,nombre,precio,precioPublico,cantidad,numCategoria)
            VALUES
                (?,?,?,?,?,?);
            """
            QuerisSQLite.ejecutarQuery(conexion,crearProductoQuery,productoTuple)
            print(datosValidados)
            self.ids.rv_inventario.data.append(datosValidados)
            self.ids.rv_inventario.refresh_from_data()
        else:
            ventanaAgregar=VentanaProductosInventario(self.agregarProducto)
            ventanaAgregar.abrir(True,False)

    def modificarProducto(self, modificar=False, datosValidados=None):
        indice=self.ids.rv_inventario.articuloSeleccionado()
        if modificar==True:
            productoTuple=(datosValidados["nombre"],datosValidados["precio"],datosValidados["precioPublico"],datosValidados["cantidad"],datosValidados["numDeCategoria"],datosValidados["codigo"])
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            actualizarProductoQuery="""
            UPDATE
                productos
            SET
                nombre=?, precio=?, precioPublico=?, cantidad=?, numCategoria=?
            WHERE
                codigo=? 
            """
            QuerisSQLite.ejecutarQuery(conexion,actualizarProductoQuery,productoTuple)
            self.ids.rv_inventario.data[indice]["nombre"]=datosValidados["nombre"]
            self.ids.rv_inventario.data[indice]["precio"]=datosValidados["precio"]
            self.ids.rv_inventario.data[indice]["precioPublico"]=datosValidados["precioPublico"]
            self.ids.rv_inventario.data[indice]["cantidad"]=datosValidados["cantidad"]
            self.ids.rv_inventario.data[indice]["numDeCategoria"]=datosValidados["numDeCategoria"]
            self.ids.rv_inventario.data[indice]["Categoria"]=datosValidados["Categoria"]
            print(datosValidados)
            self.ids.rv_inventario.refresh_from_data()
        else:
            if indice>=0:
                producto_a_modificar=self.ids.rv_inventario.data[indice]
                ventanaAgregar=VentanaProductosInventario(self.modificarProducto)
                ventanaAgregar.abrir(False,True,producto_a_modificar)

    def eliminarProducto(self):
        indice=self.ids.rv_inventario.articuloSeleccionado()
        if indice>=0:
            productoEliminado=(self.ids.rv_inventario.data[indice]["codigo"],)
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            eliminarProductoQuery="DELETE from productos WHERE codigo=?"
            QuerisSQLite.ejecutarQuery(conexion,eliminarProductoQuery,productoEliminado)
            self.ids.rv_inventario.data.pop(indice)
            self.ids.rv_inventario.refresh_from_data()

    def ventanaCategorias(self):
        ventanaCategorias = VentanaCategoriasInventario()
        ventanaCategorias.cargarCategoriasRV()
        ventanaCategorias.open()

    def actualizarInventario(self, nuevasCantidades):
        for prodcutoNuevo in nuevasCantidades:
            for productoViejo in self.ids.rv_inventario.data:
                if prodcutoNuevo["codigo"]==productoViejo["codigo"]:
                    productoViejo["cantidad"]=prodcutoNuevo["cantidad"]
        self.ids.rv_inventario.refresh_from_data()
        
    def cerrarSesion(self):
        self.parent.parent.current='scrn_login'

    def reportes(self):
        self.parent.parent.current='scrn_reportes'    

    def usuarios(self):
        self.parent.parent.current='scrn_usuarios'

    def ventas(self):
        self.parent.parent.current='scrn_ventas'            
        
class InventarioApp(App):
    def build(self):
        return InventarioWindow()


if __name__ == '__main__':
    InventarioApp().run()    