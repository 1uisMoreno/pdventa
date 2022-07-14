from calendar import c
import sqlite3
from sqlite3 import Error
import time

class QuerisSQLite:
    def crearConexion(path):
        conexion = None
        try:
            conexion = sqlite3.connect(path)
            print("Conexión exitosa")
        except Error as e:
            print("Erorr al conectarse, Error: ",e)
        return conexion
    
    def ejecutarQuery(conexion, query, data):
        cursor = conexion.cursor()
        try:
            cursor.execute(query,data)
            conexion.commit()
            print("Consultar realizada exitosamente")
            return cursor.lastrowid
        except Error as e:
            print("Error al realizar consulta, Error: ",e)

    def lecturaQuery(conexion, query, data=()):
        cursor = conexion.cursor()
        res = None
        try:
            cursor.execute(query,data)
            res = cursor.fetchall()
            return res
        except Error as e:
            print("Error al realizar query de lectura, Error: ",e)
    
    def crearTablas():
        conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")

        crearTablaProductos = """
        CREATE TABLE IF NOT EXISTS categorias(
            idCategoria INTEGER PRIMARY KEY,
            categoria TEXT NOT NULL,
            temporalidad TEXT NOT NULL
        );
        """
        QuerisSQLite.ejecutarQuery(conexion,crearTablaProductos,tuple())

        crearTablaProductos = """
        CREATE TABLE IF NOT EXISTS productos(
            codigo TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            precioPublico REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            numCategoria INTEGER NOT NULL,
            FOREIGN KEY (numCategoria) REFERENCES categorias(idCategoria)
        );
        """
        QuerisSQLite.ejecutarQuery(conexion,crearTablaProductos,tuple())


        crearTablaUsuarios = """
        CREATE TABLE IF NOT EXISTS usuarios(
            idUsuario INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            tipo TEXT NOT NULL
        );
        """
        QuerisSQLite.ejecutarQuery(conexion,crearTablaUsuarios,tuple())

        crearTablaVentas="""
        CREATE TABLE IF NOT EXISTS ventas(
            idVenta INTEGER PRIMARY KEY,
            idUsuario INTEGER NOT NULL,
            totalVenta REAL NOT NULL,   
            totalProductos INTEGER NOT NULL,
            fecha TIMESTAMP,
            FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario)
        )
        """
        QuerisSQLite.ejecutarQuery(conexion,crearTablaVentas,tuple())

        crearTablaDetallesVentas="""
        CREATE TABLE IF NOT EXISTS detallesVentas(
            idDetalle INTEGER PRIMARY KEY,
            idVenta INTEGER NOT NULL,
            codigo INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,   
            cantidad INTEGER NOT NULL,
            FOREIGN KEY (idVenta) REFERENCES ventas(idVenta),
            FOREIGN KEY (codigo) REFERENCES productos(codigo)
        )
        """
        QuerisSQLite.ejecutarQuery(conexion,crearTablaDetallesVentas,tuple())

        crearTablaDescuentos="""
        CREATE TABLE IF NOT EXISTS descuentos(
            idDescuento INTEGER PRIMARY KEY,
            idVenta INTEGER NOT NULL,
            idUsuario INTEGER NOT NULL,
            totalDescuento REAL NOT NULL,
            FOREIGN KEY (idVenta) REFERENCES ventas(idVenta),
            FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario)
        )
        """
        QuerisSQLite.ejecutarQuery(conexion,crearTablaDescuentos,tuple())

if __name__ == '__main__':
    # ventas=[]
    # conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
    # ventasDetallesQuery="SELECT * from detallesVentas WHERE idVenta=?"
    # idTuple=(3,)
    # ventas_sql= QuerisSQLite.lecturaQuery(conexion, ventasDetallesQuery,idTuple)
    # if ventas_sql:
    #     for venta in ventas_sql:
    #         precioFinal=float(venta[4])*float(venta[5])
    #         ventas.append({"idDetalle":venta[0],"idVenta":venta[1],"codigo":venta[2],"nombre":venta[3],"precioIndividual":venta[4],"cantidad":venta[5],"total":precioFinal})
    # print(ventas_sql)
    # print(ventas)
    conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
    productoCompletoQuery= "SELECT * FROM productos WHERE codigo=?"
    codigoTuple = (111,)
    productoSql = QuerisSQLite.lecturaQuery(conexion, productoCompletoQuery, codigoTuple)
    print(productoSql)


    # from datetime import datetime, timedelta
    # conexion = QuerisSQLite.crearConexion("pdventaDB.sqlite")
    # fecha=datetime.today()-timedelta(days=1)
    # nuevaFechaTuple=(fecha,4)
    # actualizar = "UPDATE ventas SET fecha=? WHERE idVenta=?"
    # QuerisSQLite.ejecutarQuery(conexion,actualizar,nuevaFechaTuple)






    # insrtarProductos= """
    # INSERT INTO
    #     productos (codigo, nombre, precio, precioPublico, cantidad, numCategoria)
    # VALUES
    #     ('111', 'resistol chico', 12.50, 15.0, 10, 1),
    #     ('222', 'cartulina', 3.5, 5.0, 10, 1),
    #     ('333', 'lapiz', 4.5, 5.5, 7, 1),
    #     ('444', 'borrador', 5.0, 7.5, 10, 1),
    #     ('555', 'teclado', 150.0, 210.0, 10, 2),
    #     ('666', 'cuaderno', 22.0, 27.0, 25, 1),
    #     ('777', 'raton', 31.0, 42.5, 7, 2)
    # """
    # QuerisSQLite.ejecutarQuery(conexion,insrtarProductos,tuple())
    

    # insrtarUsuario= """
    # INSERT INTO
    #     usuarios (idUsuario,username, password, nombre, telefono, tipo)
    # VALUES
    #     (20166536,'lmoreno', '1234', 'Luis Moreno', '3121743708', 'Admin'),
    #     (19760101,'colmos', '1976', 'Celia Olmos', '3121107387', 'Admin');
    # """
    # QuerisSQLite.ejecutarQuery(conexion,insrtarUsuario,tuple())

    # insrtarCategorias= """
    # INSERT INTO
    #     categorias (idCategoria, categoria, temporalidad)
    # VALUES
    #     (1, 'PAPELERIA', 'No'),
    #     (2, 'CIBER', 'No');
    # """
    # QuerisSQLite.ejecutarQuery(conexion,insrtarCategorias,tuple())



    # insertarCambio = """
    # UPDATE
    #     usuarios
    # SET
    #     password='1234'
    # WHERE
    #     username='lmoreno'
    # """
    # QuerisSQLite.ejecutarQuery(conexion,insertarCambio,tuple())

    # borrarProducto=('222',)
    # queryBorrar = """ DELETE from productos where codigo = ?"""
    # QuerisSQLite.ejecutarQuery(conexion,queryBorrar,borrarProducto)




    # insrtarUsuario= """
    # INSERT INTO
    #     productos (codigo, nombre, precio, precioPublico, cantidad, numCategoria, categoria)
    # VALUES
    #     ('222', 'cartulina', 3.5, 5.0, 10, 1, 'PAPELERIA');
    # """
    # QuerisSQLite.ejecutarQuery(conexion,insrtarUsuario,tuple())
