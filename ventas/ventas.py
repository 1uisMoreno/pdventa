from kivy.core.window import Keyboard,Window
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang import Builder
from sqlquerys import QuerisSQLite
from datetime import datetime,timedelta

Builder.load_file('ventas/ventas.kv')

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)

class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids['_numero'].text = str(1+index)
        self.ids['_articulo'].text = data["nombre"].capitalize()
        self.ids['_cantidad'].text = str(data["cantidadCarrito"])
        self.ids['_precioUnitario'].text = str("{:.2f}".format(data["precioPublico"]))
        self.ids['_precio'].text = str("{:.2f}".format(data["precioTotalData"]))
        return super(SelectableBoxLayout, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayout, self).on_touch_down(touch):
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

class SelectableBoxLayoutVentanaNombre(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids['_codigoVentanaNombre'].text = str(data['codigo'])
        self.ids['_articuloVentanaNombre'].text = data["nombre"].capitalize()
        self.ids['_cantidadVentanaNombre'].text = str(data["cantidad"])
        self.ids['_precioVentanaNombre'].text = str("{:.2f}".format(data["precioPublico"]))
        return super(SelectableBoxLayoutVentanaNombre, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableBoxLayoutVentanaNombre, self).on_touch_down(touch):
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

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = []
        self.modificarProdcuto=None

    def agregarArticulo(self, articulo):
        articulo["seleccionado"]=False
        indice=-1
        if self.data:
            for i in range(len(self.data)):
                if articulo['codigo']==self.data[i]["codigo"]:
                    indice = i
            if indice>=0:
                self.data[indice]["cantidadCarrito"]+=1
                self.data[indice]["precioTotalData"]=self.data[indice]["precioPublico"]*self.data[indice]["cantidadCarrito"]
                self.refresh_from_data()
            else:
                self.data.append(articulo)       
        else:
            self.data.append(articulo)

    def articuloSeleccionado(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
        return indice

    def eliminarArticulo(self):
        indice= self.articuloSeleccionado()
        precio=0
        if indice>=0:
            self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
            precio = self.data[indice]['precioTotalData']
            self.data.pop(indice)
            self.refresh_from_data()
        return precio

    def cambiarArticulo(self):
        indice= self.articuloSeleccionado()
        if indice>=0:
            ventanaCambiarArticulo= VentanaCambiarArticulo(self.data[indice], self.actualizarCambio)
            ventanaCambiarArticulo.open()

    def actualizarCambio(self, cantidad):
        indice= self.articuloSeleccionado()
        if indice>=0:
            if cantidad==0:
                self.data.pop(indice)
                self._layout_manager.deselect_node(self._layout_manager._last_selected_node)
            else:
                self.data[indice]['cantidadCarrito']=cantidad
                self.data[indice]['precioTotalData']=self.data[indice]['precioPublico']*cantidad
            self.refresh_from_data()
            nuevoTotal = 0
            for datos in self.data:
                nuevoTotal+=datos['precioTotalData']
            self.modificarProdcuto(False,nuevoTotal)

class VentanaCambiarArticulo(Popup):
    def __init__(self, articuloData, apuntadorActualizarCambio, **kwargs):
        super(VentanaCambiarArticulo, self).__init__(**kwargs)
        self.articuloData = articuloData
        self.actualizarCambio= apuntadorActualizarCambio
        self.ids.productoCambiar.text=self.articuloData['nombre'].capitalize()
        self.ids.cantidadCambiar.text=str(self.articuloData['cantidadCarrito'])
        self.ids.cantidadNueva.disabled=True

    def validarNuevaCantidad(self, cantidadNueva, boton=None):
        try:
            cantidadNueva= int(cantidadNueva)
            if cantidadNueva<=0:    
                self.ids.notificacionCantidadCambiada.text= 'Cantidad no valida'
                self.ids.cantidadNueva.disabled=True
            else:
                conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
                codigo=self.articuloData['codigo']
                queryCantidad = "SELECT codigo, cantidad from productos"
                codigos_cantidades = QuerisSQLite.lecturaQuery(conexion,queryCantidad)
                if codigos_cantidades:
                    for i in codigos_cantidades:
                        if i[0]==codigo:
                            if i[1]>0:
                                if cantidadNueva<=i[1]:
                                    self.ids.cantidadNueva.disabled=False
                                    self.ids.notificacionCantidadCambiada.text= ''
                                    if boton==True:
                                        self.actualizarCambio(cantidadNueva)
                                        self.dismiss()
                                else:
                                    self.ids.notificacionCantidadCambiada.text= 'Cantidad no existente'
                                    self.ids.cantidadNueva.disabled=True
                            else:
                                self.ids.notificacionCantidadCambiada.text= 'Cantidad no existente'
                                self.ids.cantidadNueva.disabled=True           
        except:
            self.ids.notificacionCantidadCambiada.text= 'Cantidad no valida'
            self.ids.cantidadNueva.disabled=True

class ventanaProductoNombre(Popup):
    def __init__(self, inputNombre, apuntadoragregacionDeProducto, **kwargs):
        super(ventanaProductoNombre, self).__init__(**kwargs)
        self.inputNombre = inputNombre
        self.agregacionDeProducto = apuntadoragregacionDeProducto

    def mostrarArticulos(self):
        self.open()
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        queryProdcutos = "SELECT * from productos"
        inventario = QuerisSQLite.lecturaQuery(conexion,queryProdcutos)
        if inventario:
            for nombre in inventario:
                if nombre[1].lower().find(self.inputNombre)>=0:
                    producto = {'codigo':nombre[0], 'nombre': nombre[1], 'precioPublico': nombre[3], 'cantidad': nombre[4] }
                    self.ids.rvs.agregarArticulo(producto)   

    def seleccionarArticulo(self):
        indice = self.ids.rvs.articuloSeleccionado()
        if indice>=0:
            _articulo = self.ids.rvs.data[indice]
            articulo={}
            articulo['codigo']=_articulo['codigo']
            articulo['nombre']=_articulo['nombre']
            articulo['precioPublico']=_articulo['precioPublico']
            articulo["cantidadCarrito"]=1
            articulo["cantidadInventario"]=_articulo["cantidad"]
            articulo["precioTotalData"]=_articulo["precioPublico"]
            if callable(self.agregacionDeProducto):
                self.agregacionDeProducto(articulo) 
            self.dismiss()

class VentanaPagar(Popup):
    def __init__(self, total, apuntadorPagado, **kwargs):
        super(VentanaPagar, self).__init__(**kwargs)
        self.pagoRealizado=apuntadorPagado
        self.total = total

    def mostrarPago(self, dineroRecibido=0):
        print(dineroRecibido)
        self.open()
        self.ids.total_ventana_Pagar.text= str(self.total)
        self.ids.botonPagar.disabled=True
        
    def mostrarCambio(self, dineroRecibido=0, boton=None):
        dineroRecibido= float(dineroRecibido)
        if dineroRecibido>=self.total:
            self.ids.cambio_ventana_pago.text= str(dineroRecibido-self.total)
            self.ids.botonPagar.disabled=False
            if boton==True:
                self.pagarVentanaPagar()
        else:
            self.ids.cambio_ventana_pago.text= '---'
            self.ids.botonPagar.disabled=True

    def pagarVentanaPagar(self):
        self.pagoRealizado()
        self.dismiss()

class VentasWindow(BoxLayout):
    usuario=None
    def __init__(self, apuntador_Actualizar_Inventario,**kwargs):
        super().__init__(**kwargs)
        self.actualizarInventario=apuntador_Actualizar_Inventario
        self.total=0.0
        self.totalProductos=0
        self.ids.rvs.modificarProdcuto = self.cambiarProducto
        self.fecha = datetime.now()
        self.ids.label_fecha.text = self.fecha.strftime("%d/%m/%y")
        Clock.schedule_interval(self.actualizarHora,1)

    def actualizarHora(self, *args):
        self.fecha = self.fecha+timedelta(seconds=1)
        self.ids.label_hora.text = self.fecha.strftime("%H:%M:%S")

    def agregarProductoCodigo(self, codigo):
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        queryProdcutos = "SELECT * from productos"
        inventario = QuerisSQLite.lecturaQuery(conexion,queryProdcutos)
        no_existencia=True
        if inventario:
            for producto in inventario:
                if codigo==producto[0]:
                    no_existencia=False
                    articulo={}
                    articulo["codigo"]=producto[0]
                    articulo["nombre"]=producto[1]
                    articulo["precio"]=producto[2]
                    articulo["precioPublico"]=producto[3]
                    articulo["cantidadCarrito"]=1
                    articulo["cantidadInventario"]=producto[4]
                    articulo["precioTotalData"]=producto[3]
                    if producto[4]<=0:
                        self.ids.TextoError.text= 'El producto no tiene existencias'
                        self.ids.buscarCodigo.text=''
                        break
                    else:
                        self.agregacionDeProducto(articulo)
                        self.ids.buscarCodigo.text=''
                        self.ids.TextoError.text= ''
                        break 
        if no_existencia==True:
            self.ids.TextoError.text= 'Producto no encontrado'

    def agregarProductoNombre(self, nombre):
        self.ids.buscarNombre.text=''
        self.ids.TextoError.text= ''
        ventanaNombre= ventanaProductoNombre(nombre, self.agregacionDeProducto)
        ventanaNombre.mostrarArticulos()

    def agregacionDeProducto(self, articulo):
        self.total = self.total + articulo["precioPublico"]
        self.ids.labelSubTotal.text = "$ {:.2f}".format(self.total)
        self.ids.rvs.agregarArticulo(articulo)
    
    def inventario(self):
        self.parent.parent.current='scrn_inventario'

    def cerrarSesion(self):
        self.parent.parent.current='scrn_login'

    def eliminarProducto(self):
        self.ids.TextoError.text= ''
        precio= self.ids.rvs.eliminarArticulo()
        self.total-=precio
        self.ids.labelSubTotal.text = "$ {:.2f}".format(self.total)

    def cambiarProducto(self, cambio=True, NuevoTotal=None):
        if cambio:
            self.ids.rvs.cambiarArticulo()
            self.ids.TextoError.text= ''
        else:
            self.total=NuevoTotal
            self.ids.labelSubTotal.text = "$ {:.2f}".format(self.total)
            self.ids.TextoError.text= ''

    def pagar(self):
        if self.ids.rvs.data:
                ventanaPagar=VentanaPagar(self.total, self.pagado)
                ventanaPagar.mostrarPago()
        else:  
            self.ids.TextoError.text= 'No hay nada que pagar'

    def pagado(self):
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        for articulo in self.ids.rvs.data:
            if articulo["cantidadCarrito"]>=0:
                self.totalProductos+=articulo['cantidadCarrito']

        queryCanitdadNueva="UPDATE productos SET cantidad=? WHERE codigo=?"

        ventaQuery="INSERT INTO ventas (idUsuario, totalVenta, totalProductos, fecha) VALUES (?, ?, ?, ?)"
        ventaTuple=(self.usuario['idUsuario'],self.total, self.totalProductos, self.fecha)
        venta_id=QuerisSQLite.ejecutarQuery(conexion,ventaQuery,ventaTuple)

        detalleQuery="INSERT INTO detallesVentas (idVenta, codigo, nombre, precio, cantidad) VALUES (?, ?, ?, ?, ?)"

        actualizarInventario=[]
        for articulo in self.ids.rvs.data:
            cantidadNueva=0
            if articulo['cantidadInventario']-articulo['cantidadCarrito']>=0:
                cantidadNueva=articulo['cantidadInventario']-articulo['cantidadCarrito']
            tupleCantidadNueva=(cantidadNueva,articulo['codigo'])
            detalleTuple=(venta_id,articulo["codigo"],articulo["nombre"],articulo["precioPublico"],articulo["cantidadCarrito"])
            QuerisSQLite.ejecutarQuery(conexion,detalleQuery,detalleTuple)
            QuerisSQLite.ejecutarQuery(conexion,queryCanitdadNueva,tupleCantidadNueva)

            actualizarInventario.append({'codigo': articulo["codigo"],"cantidad":cantidadNueva})    
        self.actualizarInventario(actualizarInventario)

        self.total=0
        self.totalProductos=0
        self.ids.buscarCodigo.disabled=True
        self.ids.buscarNombre.disabled=True
        self.ids.pagar.disabled=True
        self.ids.cambiarCantidad.disabled=True
        self.ids.eliminarArticulo.disabled=True
        self.ids.TextoExito.text= 'Compra realizada con exito'
        self.ids.TextoError.text= ''

    def nuevaCompra(self):
        self.total=0
        self.ids.rvs.data=[]
        self.ids.rvs.refresh_from_data()
        self.ids.buscarCodigo.disabled=False
        self.ids.buscarNombre.disabled=False
        self.ids.pagar.disabled=False
        self.ids.cambiarCantidad.disabled=False
        self.ids.eliminarArticulo.disabled=False
        self.ids.TextoExito.text= ''
        self.ids.TextoError.text= ''
        self.ids.labelSubTotal.text =  "$ 0.00"

    def guardarUsuario(self, usuario):
        self.ids.label_bienvenido.text= 'Bienvenido: '+usuario["nombre"]
        self.usuario=usuario

class VentasApp(App):
    def build(self):
        return VentasWindow()

if __name__ == '__main__':
    VentasApp().run()
