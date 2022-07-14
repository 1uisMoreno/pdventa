from dataclasses import field
from datetime import datetime
from functools import total_ordering
from re import S
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
from kivy.uix.popup import Popup
from sqlquerys import QuerisSQLite
from datetime import datetime, timedelta
import csv
Builder.load_file('reportes/reportes.kv')

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    touch_deselect_last = BooleanProperty(True)
# ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# RV detalles y ventana detalles

class SelectableDatallesLabel(RecycleDataViewBehavior, BoxLayout):
    index = None

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.ids['_idDetalle'].text = str(data["idDetalle"])
        self.ids['_idVenta'].text = str(data["idVenta"])
        self.ids['_codigo'].text = str(data["codigo"])
        self.ids['_nombre'].text = str(data["nombre"])
        self.ids['_precioIndividual'].text = str(data["precioIndividual"])
        self.ids['_cantidad'].text = str(data["cantidad"])
        self.ids['_total'].text = str(data["total"])
        return super(SelectableDatallesLabel, self).refresh_view_attrs(
            rv, index, data)

class RV_detalles(RecycleView):
    def __init__(self, **kwargs):
        super(RV_detalles, self).__init__(**kwargs)

class VentanaDetalles(Popup):
    def __init__(self, **kwargs):
        super(VentanaDetalles, self).__init__(**kwargs)
        self.data = []
    
    def mostrar(self,venta):
        self.open()
        ventas=[]
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        ventasDetallesQuery="SELECT * from detallesVentas WHERE idVenta=?"
        idTuple=(venta['idVenta'],)
        ventas_sql= QuerisSQLite.lecturaQuery(conexion, ventasDetallesQuery,idTuple)
        if ventas_sql:
            for venta in ventas_sql:
                precioFinal=float(venta[4])*float(venta[5])
                ventas.append({"idDetalle":venta[0],"idVenta":venta[1],"codigo":venta[2],"nombre":venta[3],"precioIndividual":venta[4],"cantidad":venta[5],"total":precioFinal})
        
        for data in ventas:
            self.ids.rv_detalles.data.append(data)
        self.ids.rv_detalles.refresh_from_data()

# ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# RV ventas

class SelectableReporteVentasLabel(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids['_idVenta'].text = str(data["idVenta"])
        self.ids['_idUsuario'].text = str(data["idUsuario"])
        self.ids['_productosVendidos'].text = str(data["productosVendidos"])
        self.ids['_total'].text = str(data["totalVendido"])
        self.ids['_hora'].text = str(data["fecha"].strftime("%H:%M:%S"))
        self.ids['_fecha'].text = str(data["fecha"].strftime("%d/%m/%Y"))


        return super(SelectableReporteVentasLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableReporteVentasLabel, self).on_touch_down(touch):
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

class RV_reportes_ventas(RecycleView):
    def __init__(self, **kwargs):
        super(RV_reportes_ventas, self).__init__(**kwargs)
        self.data = []
#{"idVenta":58987,"idUsuario":20166536,"productosVendidos":6,"total":500,"hora":"12:20","fecha":"10/05/2022"}
    def agregarDatos(self, datos):
        for dato in datos:
            dato['seleccionado']=False
            self.data.append(dato)
        self.refresh_from_data()

    def ventaSeleccionada(self):
        indice=-1
        for i in range(len(self.data)):
            if self.data[i]['seleccionado']:
                indice=i
                break
        return indice

# ████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████

# Ventana Reportes

class ReportesWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def ventanaDetalles(self):
        indice=self.ids.rv_reportes_ventas.ventaSeleccionada()
        if indice>=0:
            ventanaDetalles=VentanaDetalles()
            ventanaDetalles.mostrar(self.ids.rv_reportes_ventas.data[indice])

    def observaciones(self):
        pass

    def guardarCSV(self):    
        if self.ids.rv_reportes_ventas.data:
            print("Guardar CSV")
            print(self.ids.rv_reportes_ventas.data)
            conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
            ventasDetallesQuery="SELECT * from detallesVentas WHERE idVenta=?"
            if self.ids.labelFechaFinal.text:
                nombreCSV="ventasCSV/"+self.ids.labelFechaInicial.text+" -- "+self.ids.labelFechaFinal.text+".csv"
            else:
                nombreCSV="ventasCSV/"+self.ids.labelFechaInicial.text+".csv"

            productosCSV=[]
            ventasLista = []
            totalVendidoCSV=0
            totalGanancia=0
            for venta in self.ids.rv_reportes_ventas.data:
                idTuple=(venta['idVenta'],)
                ventas_sql = QuerisSQLite.lecturaQuery(conexion, ventasDetallesQuery,idTuple)
                ventasLista.append(ventas_sql)
            print("Ventas Lista",ventasLista)
            for ventaList in ventasLista:
                print("Venta Individual",ventaList)
                for productoVendidoTuple in ventaList:
                    print("Producto Tuple: ",productoVendidoTuple)
                    productoCompletoQuery= "SELECT * FROM productos WHERE codigo=?"
                    codigoTuple = (productoVendidoTuple[2],)
                    productoSql = QuerisSQLite.lecturaQuery(conexion, productoCompletoQuery, codigoTuple)
                    articuloEncontrado = next((articulo for articulo in productosCSV if articulo["Codigo"]==productoVendidoTuple[2]),None)
                    totalVendidoCSV+=productoVendidoTuple[4]*productoVendidoTuple[5]
                    cantidad=productoVendidoTuple[5]
                    diferencia= productoVendidoTuple[4]-productoSql[0][2]
                    totalGanancia+=cantidad*diferencia 
                    print("Articulo Encontrado", articuloEncontrado)
                    print("Total Vendido",totalVendidoCSV)
                    if articuloEncontrado:
                        articuloEncontrado["Cantidad"]+=productoVendidoTuple[5]
                        articuloEncontrado["Precio Total"]+=productoVendidoTuple[4]*productoVendidoTuple[5]
                        articuloEncontrado["Ganancia Total"]+=cantidad*diferencia    
                    else:
                        gananciaProducto=cantidad*diferencia  
                        productosCSV.append({"Codigo": productoVendidoTuple[2], "Nombre":productoVendidoTuple[3],"Precio":productoSql[0][2], "Precio Publico":productoVendidoTuple[4],"Cantidad":productoVendidoTuple[5],"Precio Total":productoVendidoTuple[4]*productoVendidoTuple[5], "Ganancia Total":gananciaProducto})
            encabezados=["Codigo","Nombre","Precio","Precio Publico","Cantidad","Precio Total","Ganancia Total"]
            pie=[{"Precio Total":totalVendidoCSV, "Ganancia Total":totalGanancia}]
            with open(nombreCSV, "w", encoding="UTF8",newline="") as archivo:
                writer=csv.DictWriter(archivo, fieldnames=encabezados)
                writer.writeheader()
                writer.writerows(productosCSV)
                writer.writerows(pie)
            self.ids.labelNotificacion.text= 'CSV creado exitosamente'
            print("ProductosCSV:",productosCSV)
            print("Nombre archivo CSV",nombreCSV)
        else:
            print("RV vacio")

    def inventario(self):
        self.parent.parent.current='scrn_inventario'

    def usuarios(self):
        self.parent.parent.current='scrn_usuarios'

    def ventas(self):
        self.parent.parent.current='scrn_ventas'

    def cerrarSesion(self):
        self.parent.parent.current='scrn_login'

    def cargarVentasRV(self, opcion=None):
        self.ids.rv_reportes_ventas.data=[]
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
        entradaValida=True
        final_sum=0
        fechaInicio=datetime.strptime('01/01/00', '%d/%m/%y')
        fechaFin=datetime.strptime('31/12/2099','%d/%m/%Y')

        ventas=[]

        ventasQuery="""SELECT * from ventas WHERE fecha BETWEEN ? AND ?"""

        if opcion=='Dia':
            if self.ids.fechaUnicaVentanaReportes.text:
                print(self.ids.fechaUnicaVentanaReportes.text)
                fecha=self.ids.fechaUnicaVentanaReportes.text
                try:
                    fechaElegida=datetime.strptime(fecha,'%d/%m/%y')
                except:
                    entradaValida=False
                if entradaValida:
                    fechaInicio=fechaElegida
                    fechaFin=fechaElegida+timedelta(days=1)
                    self.ids.labelFechaInicial.text=str(fechaInicio.strftime('%d-%m-%y'))
            else:
                fechaInicio=datetime.today().date()
                fechaFin=fechaInicio+timedelta(days=1)
                self.ids.labelFechaInicial.text=str(fechaInicio.strftime('%d-%m-%y'))
            self.ids.separadorFechas.text=''
            self.ids.fechaLabel.text='Fecha: '
            self.ids.labelFechaFinal.text=''
        if opcion=='Rango':
            if self.ids.rangoFechaInicioVentanaReportes.text:
                fecha=self.ids.rangoFechaInicioVentanaReportes.text
                try:
                    fechaInicio=datetime.strptime(fecha,'%d/%m/%y')
                except:
                    entradaValida=False
            if self.ids.rangoFechaFinVentanaReportes.text:
                fecha=self.ids.rangoFechaFinVentanaReportes.text
                try:
                    fechaFin=datetime.strptime(fecha,'%d/%m/%y')
                    fechaFin=fechaFin+timedelta(days=1)
                except:
                    entradaValida=False
            if entradaValida:
                self.ids.labelFechaInicial.text=str(fechaInicio.strftime('%d-%m-%y'))
                fechaFinLabel=fechaFin-timedelta(days=1)
                self.ids.labelFechaFinal.text=str(fechaFinLabel.strftime('%d-%m-%y'))
            self.ids.separadorFechas.text='--'
            self.ids.fechaLabel.text='Fechas: '
        if entradaValida:
            fecha_Inicio_Fin=(fechaInicio,fechaFin)
            ventas_sql=QuerisSQLite.lecturaQuery(conexion,ventasQuery,fecha_Inicio_Fin)
            if ventas_sql:
                for venta in ventas_sql:
                    final_sum+=venta[2]
                    ventas.append({"idVenta":venta[0],"idUsuario":venta[1],"totalVendido":venta[2],"productosVendidos":venta[3],"fecha":datetime.strptime(venta[4],'%Y-%m-%d %H:%M:%S.%f')})
                self.ids.rv_reportes_ventas.agregarDatos(ventas)
        self.ids.labelTotalVendido.text= '$ '+str('{:.2f}'.format(final_sum))
        self.ids.rangoFechaInicioVentanaReportes.text=''
        self.ids.rangoFechaFinVentanaReportes.text=''
        self.ids.fechaUnicaVentanaReportes.text=''

class ReportesApp(App):
    def build(self):
        return ReportesWindow()


if __name__ == '__main__':
    ReportesApp().run()