# Universidad del Valle de Guatemala
# Graficas por Computadora - Seccion 10
# Maria Fernanda Estrada 14198
# Cargar un archivo obj y leer/mostrar lo que lleva dentro
# Codigo base en ejemplo visto en clase





import struct
import Funciones2 as imagen
from random import randint
from collections import namedtuple
from math import sin, cos

# Vectores
V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])


# Clase que carga el obj, lee el obj y dibuja el modelo
class Obj(object):

    # Constructor
    def __init__(self, filename, filenameMaterial = None):
        # Para leer el archivo
        with open(filename) as f:
            self.lines = f.read().splitlines()
        # Para leer el archivo de materiales
        if filenameMaterial:
            with open(filenameMaterial) as f:
                self.linesMtl = f.read().splitlines()
        # Inicializar todo en cero y leer
        self.vertices = []
        self.tvertices = []
        self.nvertices = []
        self.caras = []
        self.materialesDic = {} # Diccionario de colores
        self.read()
        self.readMtl()

    
    # Leer e interpretar el archivo obj
    def read(self):
        materialActual = ''
        # Para cada linea leida en el documento
        for line in self.lines:
            # Si no esta vacia hacer lo siguiente
            if line:
                # Separar la primera letra del resto. Lo primero es el prefix v (vertice) o f (cara).
                prefix, value = line.split(' ', 1) # Se coloca 1 para que tome 1 linea a la vez
                # Si es un vertice, colocar en el array de vertices
                if prefix == 'v':
                    # Separa los valores despues de la v por espacios, los mapea a un float (cast) y los vuelve una lista despues a los tres
                    listaV = list(map(float, value.split(' ')))
                    self.vertices.append(listaV)
                # Si es un vertice de textura, colocar en el array de vertices de textura
                elif prefix == 'vt':
                    # Separa los valores despues de la vt por espacios, los mapea a un float (cast) y los vuelve una lista despues a los tres
                    listaVt = list(map(float, value.split(' ')))
                    self.tvertices.append(listaVt)
                elif prefix == 'vn':
                    # Separa los valores despues de la vt por espacios, los mapea a un float (cast) y los vuelve una lista despues a los tres
                    listaVN = list(map(float, value.split(' ')))
                    self.nvertices.append(listaVN)
                # Si es una cara, colocar en el array de caras. Este sera un array de arrays
                elif prefix == 'f':
                    # Separar por espacio
                    listaF1 = value.split(' ')
                    listaX = []
                    # Ahora separar por guiones y castear a int
                    for cara in listaF1:
                        listaF2 = cara.split('/')
                        listaF = []
                        for l2 in listaF2:
                            if l2:
                                listaF.append(int(l2))
                            else:
                                listaF.append(0)
                        # Se guarda el material antes de las caras a las que se aplicaran
                        listaF.append(materialActual)
                        listaX.append(listaF)
                    self.caras.append(listaX)
                # Para ver que material es el que toca a ciertas caras
                elif prefix == 'usemtl':
                    materialActual = value

    # Leer e interpretar el archivo mtl
    def readMtl(self):
        # Guardar el nombre del material
        nombreMaterial = ''
        for line in self.linesMtl:
             # Si no esta vacia hacer lo siguiente
            if line:
                prefix, value = line.split(' ', 1) # Se coloca 1 para que tome 1 linea a la vez
                # Guardar el nombre de material
                if prefix == 'newmtl':
                    nombreMaterial = value
                # Guardar los valores rgb de ese material en un diccionario
                elif prefix == 'Kd':
                    coloresStr = value.split(' ')
                    listaColores = list(map(float, coloresStr))
                    self.materialesDic[nombreMaterial] = listaColores

    # Funcion para modificar cada vector dado
    def transformar(self, vertice):

        # Se define un vector de 4 dimensiones al agregarle un 1 al final
        vertice4D = [[vertice.x, 0, 0, 0], 
                     [vertice.y, 0, 0, 0], 
                     [vertice.z, 0, 0, 0], 
                     [1, 0, 0, 0]]
        # Se aplican todas las matrices de transformacion
        vertice_t = imagen.matrixMult(self.ViewPort, imagen.matrixMult(self.Perspectiva, imagen.matrixMult(self.View, imagen.matrixMult(self.Modelo, vertice4D))))

        # Ahora,  que ya se transformo el vertice, se debe regresar a 3D. Se divide por la cuarta componente
        vertice_t = [int((vertice_t[0][0]/vertice_t[3][0])),
                     int((vertice_t[1][0]/vertice_t[3][0])),
                     int((vertice_t[2][0]/vertice_t[3][0]))]
        return V3(*vertice_t)

    # Mandar los vertices y caras a la funcion glLine (en valores de -1 a 1 para traslacion y escala) (valores de 0 a 1 para textura)
    def load(self, traslacion = (0, 0, 0), escala = (1, 1, 1), rotacion = (0, 0, 0), textura = None):

        # Generar matriz de modelo ya modificado y del viewport
        self.PipelineModelo(traslacion, escala, rotacion)
        self.PipelineViewPort()

        luz = V3(0, 0, 1) # La luz solo vendra hacia la pantalla, eje z

        for cara in self.caras:
            # Se agrega el valor en z que nos interesa para el zbuffer
            x1 = (self.vertices[cara[0][0] - 1][0])
            y1 = (self.vertices[cara[0][0] - 1][1])
            z1 = (self.vertices[cara[0][0] - 1][2])
            x2 = (self.vertices[cara[1][0] - 1][0])
            y2 = (self.vertices[cara[1][0] - 1][1])
            z2 = (self.vertices[cara[1][0] - 1][2])
            x3 = (self.vertices[cara[2][0] - 1][0])
            y3 = (self.vertices[cara[2][0] - 1][1])
            z3 = (self.vertices[cara[2][0] - 1][2])

            # Ya con los valores convertidos, se crean los vectores v1, v2 y v3
            v1 = self.transformar(V3(x1, y1, z1))
            v2 = self.transformar(V3(x2, y2, z2))
            v3 = self.transformar(V3(x3, y3, z3))

            nx1 = self.nvertices[cara[0][2] - 1][0]
            ny1 = self.nvertices[cara[0][2] - 1][1]
            nz1 = self.nvertices[cara[0][2] - 1][2]
            nx2 = self.nvertices[cara[1][2] - 1][0]
            ny2 = self.nvertices[cara[1][2] - 1][1]
            nz2 = self.nvertices[cara[1][2] - 1][2]
            nx3 = self.nvertices[cara[2][2] - 1][0]
            ny3 = self.nvertices[cara[2][2] - 1][1]
            nz3 = self.nvertices[cara[2][2] - 1][2]

            n1 = V3(nx1, ny1, nz1)
            n2 = V3(nx2, ny2, nz2)
            n3 = V3(nx3, ny3, nz3)

            # Si no hay textura, colocar el color de los materiales
            if not textura:
                # Pintar el color del material guardado por la intensidad para darle luz
                colorbg = V3(self.materialesDic[cara[0][3]][0], self.materialesDic[cara[0][3]][1], self.materialesDic[cara[0][3]][2])
                imagen.triangle(v1, v2, v3, n1, n2, n3, colorbg)
            else:
                # Como los valores en la textura van de 0 a 1, ya no se necesitan convertir. Solo se resta 1 porque comienza en 1
                eq1 = int(textura.width * ((self.tvertices[cara[0][1] - 1][0]))) - 1
                ye1 = int(textura.height * ((self.tvertices[cara[0][1] - 1][1]))) - 1
                eq2 = int(textura.width * ((self.tvertices[cara[1][1] - 1][0]))) - 1
                ye2 = int(textura.height * ((self.tvertices[cara[1][1] - 1][1]))) - 1
                eq3 = int(textura.width * ((self.tvertices[cara[2][1] - 1][0]))) - 1
                ye3 = int(textura.height * ((self.tvertices[cara[2][1] - 1][1]))) - 1

                # Se crean los nuevos vectores de texturas
                t1 = V3(eq1, ye1, 0)
                t2 = V3(eq2, ye2, 0)
                t3 = V3(eq3, ye3, 0)

                # Hacer el triangulo
                imagen.triangle(v1, v2, v3, n1, n2, n3, t1, t2, t3, textura)

    # Funcion que manda en donde se encuentra la camara
    def VistaCam(self, observador, centro, arriba):

        # La definicion de cada ecuacion se vio en clase de forma grafica
        z = imagen.norm(imagen.resta(observador, centro))
        x = imagen.norm(imagen.cruz(arriba, z))
        y = imagen.norm(imagen.cruz(z, x))

        # Llamar a las matrices
        # El coeficiente para la perspectiva es estandar
        self.PipelineView(x, y, z, centro)
        self.PipelinePerspectiva(-1/(imagen.largov(imagen.resta(observador, centro))))
    
    # Se obtiene una matriz que modifica el modelo en si (se traslada, rota y escala)
    # Pasamos a WORLD SPACE, todos los puntos relativos al centro del mundo
    def PipelineModelo(self, traslacion, escala, rotacion):
        
        # Como los parametros se pasan como puntos, se deben convertir a V3
        traslacion = V3(*traslacion)
        escala = V3(*escala)
        rotacion = V3(*rotacion)

        # Matriz de traslacion (se mostro en la pp la matriz)
        traslacion_m = [[1, 0, 0, traslacion.x],
                        [0, 1, 0, traslacion.y],
                        [0, 0, 1, traslacion.z],
                        [0, 0, 0, 1]]

        # Matriz de escala (se mostro en la pp la matriz)
        escala_m = [[escala.x, 0, 0, 0],
                    [0, escala.y, 0, 0],
                    [0, 0, escala.z, 0],
                    [0, 0, 0, 1]]
        
        # Definir angulos de rotacion
        ax = rotacion.x
        ay = rotacion.y
        az = rotacion.z

        # Matriz X de rotacion (se mostro en la pp la matriz)
        rotacion_mX = [[1, 0, 0, 0],
                      [0, cos(ax), -sin(ax), 0],
                      [0, sin(ax), cos(ax), 0],
                      [0, 0, 0, 1]]
        
        # Matriz Y de rotacion (se mostro en la pp la matriz)
        rotacion_mY = [[cos(ay), 0, sin(ay), 0],
                      [0, 1, 0, 0],
                      [-sin(ay), 0, cos(ay), 0],
                      [0, 0, 0, 1]]
        
        # Matriz Z de rotacion (se mostro en la pp la matriz)
        rotacion_mZ = [[cos(az), -sin(az), 0, 0],
                      [sin(az), cos(az), 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]]
        
        # Matriz de rotacion total (se mostro en la pp la matriz)
        rotacion_m = imagen.matrixMult(rotacion_mX, imagen.matrixMult(rotacion_mY, rotacion_mZ))

        # Generar la matriz con las operaciones deseadas
        self.Modelo = imagen.matrixMult(traslacion_m, imagen.matrixMult(rotacion_m, escala_m))

    # Se obtiene una matriz que modifica el origen de la vista
    # Pasamos a CAMERA SPACE, todos los puntos relativos a la posicion de la camara
    def PipelineView(self, x, y, z, centro):

        # Como los parametros se pasan como puntos, se deben convertir a V3
        x = V3(*x)
        y = V3(*y)
        z = V3(*z)
        centro = V3(*centro)

        # Matriz inversa M vista en pp
        M = [[x.x, x.y, x.z, 0],
             [y.x, y.y, y.z, 0],
             [z.x, z.y, z.z, 0],
             [0, 0, 0, 1]]

        # Matriz para definir origen de camara vista en pp
        O = [[1, 0, 0, -centro.x],
             [0, 1, 0, -centro.y],
             [0, 0, 1, -centro.z],
             [0, 0, 0, 1]]
        
        # Matriz de view
        self.View = imagen.matrixMult(M, O)

    # Se agrega perspectiva al modelo
    def PipelinePerspectiva(self, coeficiente):
    
        # Matriz perspectiva al modelo
        self.Perspectiva = [[1, 0, 0, 0],
                           [0, 1, 0, 0],
                           [0, 0, 1, 0],
                           [0, 0, coeficiente, 1]]

    # Por ultimo, se modifica el viewport donde se dibujara el modelo
    def PipelineViewPort(self, x = 0, y = 0):
        self.ViewPort = [[imagen.bm.width/2, 0, 0, x + imagen.bm.width/2],
                         [0, imagen.bm.height/2, 0, y + imagen.bm.height/2],
                         [0, 0, 128, 128],
                         [0, 0, 0, 1]]



# Clase para colocar una textura sobre el modelo
class Texture(object):

    # Inicializar
    def __init__(self, path):
        self.path = path
        self.read()
    
    # Leer archivo de textura (visto en clase)
    def read(self):
        # Se debe seguir el formato de bmp
        image = open(self.path, "rb")
        image.seek(10)
        header_size = struct.unpack("=l", image.read(4))[0]
        image.seek(18)
        self.width = struct.unpack("=l", image.read(4))[0]
        self.height = struct.unpack("=l", image.read(4))[0]
        self.pixels = []
        image.seek(header_size)
        # Se lee el color de cada pixel y se guarda en un array
        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(image.read(1))
                g = ord(image.read(1))
                r = ord(image.read(1))
                self.pixels[y].append(imagen.color(r, g, b))
        image.close()

    # Obtener el color del pixel
    def get_Color(self, tx, ty):
        x = int(tx)
        y = int(ty)
        return self.pixels[y][x]

# ------------------------------------- Fondo --------------------------------

def Background(imagen):
    background = Texture('bg.bmp')
    for x in range(imagen.bm.width):
        for y in range(imagen.bm.height):
            imagen.bm.framebuffer[y][x] = background.pixels[y][x]



# ------------------------------------- Personajes --------------------------------

def Characters():
    
    # ------ FIGHTER KIRBY ------
    objFighterKirby = Obj('FighterKirby.obj', 'FighterKirby.mtl') # Cargar el contenido del obj
    # Donde se encuentra la camara en general para todos los modelos
    objFighterKirby.VistaCam(V3(0, 0, 2.5), V3(0, 0, 0), V3(0, 1, 0))
    # Dibujar el contenido del obj segun posicion en pantalla
    objFighterKirby.load((0.5, -0.2, 0), (0.5, 0.5, 0.5), (0, -0.5, 0))

    # ------ SLEEPY KIRBY ------
    objSleepKirby = Obj('SleepKirby.obj', 'SleepKirby.mtl') # Cargar el contenido del obj
    # Donde se encuentra la camara en general para todos los modelos
    objSleepKirby.VistaCam(V3(0, 0, 2.5), V3(0, 0, 0), V3(0, 1, 0))
    # Dibujar el contenido del obj segun posicion en pantalla
    objSleepKirby.load((-0.5, -0.05, 0), (0.5, 0.5, 0.5), (0, 0.3, 0))

    # ------ ICE KIRBY ------
    objIceKirby = Obj('IceKirby.obj', 'IceKirby.mtl') # Cargar el contenido del obj
    # Donde se encuentra la camara en general para todos los modelos
    objIceKirby.VistaCam(V3(0, 0, 2.5), V3(0, 0, 0), V3(0, 1, 0))
    # Dibujar el contenido del obj segun posicion en pantalla
    objIceKirby.load((-0.5, -0.85, 0), (0.2, 0.2, 0.2), (0, 0, 0))

    # ------ TORNADO KIRBY ------
    objTornadoKirby = Obj('TornadoKirby.obj', 'TornadoKirby.mtl') # Cargar el contenido del obj
    # Donde se encuentra la camara en general para todos los modelos
    objTornadoKirby.VistaCam(V3(0, 0, 2.5), V3(0, 0, 0), V3(0, 1, 0))
    # Dibujar el contenido del obj segun posicion en pantalla
    objTornadoKirby.load((0, -0.85, 0), (0.2, 0.2, 0.2), (0, 0, 0))

    # ------ WING KIRBY ------
    objWingKirby = Obj('WingKirby.obj', 'WingKirby.mtl') # Cargar el contenido del obj
    # Donde se encuentra la camara en general para todos los modelos
    objWingKirby.VistaCam(V3(0, 0, 2.5), V3(0, 0, 0), V3(0, 1, 0))
    # Dibujar el contenido del obj segun posicion en pantalla
    objWingKirby.load((0.5, -0.85, 0), (0.2, 0.2, 0.2), (0, 0, 0))






# ------ Configuracion pantalla ------
imagen.glInit() # Inicializar SR1
imagen.glCreateWindow(1000,1000) # Cambia el tamano del window a 1500x1500
imagen.glClearColor(0, 0, 0) # Cambia el color de la ventana a negro
imagen.glClear() # Clear a ventana
imagen.glViewPort(0, 0, 1000, 1000) # Especificar en donde se dibujara
Background(imagen)# Poner fondo
Characters() # Poner personajes
imagen.glFinish() # Generar la imagen