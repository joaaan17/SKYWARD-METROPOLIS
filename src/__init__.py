import importlib
import os
import mathutils
import posicion
import generar_ciudad
import random
import bpy
bl_info = {
    "name": "Control Velocidad Esfera",
    "blender": (2, 93, 0),
    "category": "Object",
    "author": "Grupo 05",
    "description": "Panel para controlar la velocidad de la esfera",
    "version": (1, 0, 0),
    "location": "View3D > Tool Shel7f > Control de Esfera",
}


try:
    import posicion
    importlib.reload(posicion)
except ImportError:
    import posicion


bpy.types.Scene.velocidad_esfera = bpy.props.FloatProperty(
    name="Velocidad de la Esfera",
    description="Controla la velocidad a la que se mueve la esfera",
    default=1.0,
    min=0.1,
    max=20.0
)

bpy.types.Scene.num_esferas = bpy.props.IntProperty(
    name="Número de Esferas",
    description="Define el número de esferas a crear",
    default=1,
    min=1,
    max=10
)

bpy.types.Scene.nturns = bpy.props.IntProperty(
    name="Número de giros ",
    description="Define el número de giros en la ruta",
    default=1,
    min=1,
    max=10
)

bpy.types.Scene.apply_random_oscillation = bpy.props.BoolProperty(
    name="Aplicar Oscilación Aleatoria",
    description="Activar o desactivar oscilación aleatoria",
    default=False
)

bpy.types.Scene.generar_coches = bpy.props.BoolProperty(
    name="Generar Coches",
    description="Activa esta opción para generar coches en lugar de esferas",
    default=False
)

bpy.types.Scene.oscillation_axes = bpy.props.EnumProperty(
    name="Ejes de Oscilación",
    description="Selecciona los ejes de aplicación de la oscilación",
    items=[('X', "Eje X", ""), ('Y', "Eje Y", ""), ('Z', "Eje Z", "")],
    options={'ENUM_FLAG'}
)

bpy.types.Scene.oscillation_amplitude = bpy.props.FloatProperty(
    name="Amplitud de Oscilación",
    description="Define la amplitud de la oscilación aleatoria",
    default=1.0,
    min=0.0,
    max=10.0
)

bpy.types.Scene.oscillation_frequency = bpy.props.FloatProperty(
    name="Frecuencia de Oscilación",
    description="Define la frecuencia de la oscilación aleatoria",
    default=0.1,
    min=0.0,
    max=5.0
)

bpy.types.Scene.control_rotacion = bpy.props.BoolProperty(
    name="Control de Rotación",
    description="Activa o desactiva el control de rotación",
    default=True
)

ruta_escena = bpy.data.filepath
directorio_escena = os.path.dirname(ruta_escena)
nombre_archivo = "car.obj"
ruta_completa = os.path.join(directorio_escena, nombre_archivo)
bpy.types.Scene.ruta_modelo_obj = bpy.props.StringProperty(
    name="Modelo 3D",
    description="Ruta al archivo .obj del modelo 3D",
    default=ruta_completa,
    subtype='FILE_PATH'
)
# Definir las opciones de la propiedad enum
eje_items = [
    ('X', 'X', 'Alinear con el eje X'),
    ('Y', 'Y', 'Alinear con el eje Y'),
    ('Z', 'Z', 'Alinear con el eje Z'),
    ('-X', '-X', 'Alinear con el eje -X'),
    ('-Y', '-Y', 'Alinear con el eje -Y'),
    ('-Z', '-Z', 'Alinear con el eje -Z')
]


def crea_ruta(nturns: int, N: int):
    """
    Genera una ruta aleatoria en una cuadrícula NxN con un número especificado de giros (nturns).

    Parámetros:
    -----------
    nturns : int
        Número de giros o cambios de dirección en la ruta.
    N : int
        Tamaño de la cuadrícula, donde las calles están numeradas de 0 a N.

    Descripción:
    ------------
    - La función crea una ruta inicializando en (0, 0) y eligiendo de manera aleatoria las calles 
    horizontales (filas) o verticales (columnas) para moverse, asegurándose de no repetir la última 
    posición en el siguiente turno.
    - Alterna entre filas y columnas en cada giro, asegurando diversidad en la trayectoria.
    - Finalmente, la ruta se fuerza para terminar en la última calle de la cuadrícula, ya sea 
    horizontal (i = N) o vertical (j = N).

    Retorno:
    --------
    list
        Una lista de posiciones `[i, j]` que representan la ruta en la cuadrícula.
"""

    # Listado de calles a elegir
    calles = set(range(N+1))

    i = 0
    j = 0
    posns = []

    # Elegimos al azar si la primera posición es en fila o columna
    fila = random.choice([True, False])
    for turn in range(nturns + 1):
        if fila:
            fila = False
            # Elección aleatoria de la siguiente calle
            i = random.choice(list(calles - {i}))
        else:
            fila = True
            # Elección aleatoria de la siguiente calle
            j = random.choice(list(calles - {j}))
        posns.append([i, j])

    # Forzamos que acabe en la última calle
    if fila:
        i = N
    else:
        j = N

    posns.append([i, j])

    return posns


def aplicar_configuracion_ciudad():
    """
    Aplica la configuración actual de la ciudad en el proyecto de Blender.

    Descripción:
    ------------
    - Actualiza el número de calles en los ejes X e Y según el valor almacenado 
    en `bpy.context.scene.numero_calles_x_y`.
    - Borra la configuración actual de la ciudad y genera una nueva utilizando 
    los valores actualizados.

    Flujo:
    ------
    1. Obtiene el número de calles desde las propiedades de la escena en Blender.
    2. Llama al método `Borrar_Ciudad()` para eliminar la configuración existente.
    3. Llama al método `register()` para generar la nueva configuración basada 
    en los valores actualizados.

    Notas:
    ------
    - El módulo `generar_ciudad` maneja la lógica completa de generación 
    de la ciudad.

    Retorno:
    --------
    Ninguno.
"""

    generar_ciudad.numero_calles_x = bpy.context.scene.numero_calles_x_y
    generar_ciudad.numero_calles_y = bpy.context.scene.numero_calles_x_y
    generar_ciudad.tam_calle = bpy.context.scene.amplitud_calle
    generar_ciudad.Borrar_Ciudad()  # Genera la ciudad con los nuevos valores
    generar_ciudad.register()  # Genera la ciudad con los nuevos valores


def CrearEsferas(velocidad, nturns):
    """
    Esta función crea esferas (o coches en formato 3D) 
    en posiciones aleatorias en la ciudad, simulando su movimiento 
    a lo largo de una ruta definida.

    Parámetros:
    ---------
    - velocidad (float): Velocidad a la que se mueve el objeto, utilizada para 
      calcular el tiempo en frames para recorrer una calle.
    - nturns (int): Número de vueltas o puntos en la ruta a lo largo de la ciudad 
      por donde se desplazará el objeto.

    Descripción:
    ------------
    - Calcula el tiempo necesario para recorrer una calle en función de la velocidad 
    proporcionada y genera una ruta aleatoria de movimiento para cada objeto.
    - La dirección de la ruta se elige aleatoriamente, pudiendo ser Norte-Sur (N-S), 
    Este-Oeste (E-O), Oeste-Este (O-E) o Sur-Norte (S-N).
    - Si se encuentra un archivo .obj válido, lo importa y lo escala para usarlo 
    como modelo 3D, si no, se crea una esfera básica.
    - La función `crea_ruta` genera las posiciones para la trayectoria de la esfera 
    (o coche), basándose en la dirección y el número de vueltas (`nturns`).
    - Se insertan fotogramas clave en cada posición de la ruta para animar el objeto 
    a lo largo de la ciudad.

    Retorno:
    --------
    Ninguno.
    """
    # Obtener la cantidad de frames por segundo (FPS)
    fps = bpy.context.scene.render.fps
    # Calcular el tiempo en frames para recorrer una calle
    tiempo_por_calle = fps / velocidad
    posiciones = []
    generar_coches = bpy.context.scene.generar_coches

    direccion = random.randint(0, 3)  # harexmos 0 N-S y 1 E-O

    if direccion == 0:
        calle_x = random.randint(0, generar_ciudad.numero_calles_x)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_x = -2 + (calle_x * generar_ciudad.tam_calle) + \
            (calle_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = -2 + (generar_ciudad.numero_calles_y * generar_ciudad.tam_calle) + (
            generar_ciudad.numero_calles_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        if generar_coches:
            print("RUTA OBJETO CARGADA")
            ruta_obj = ruta_completa  # bpy.context.scene.ruta_modelo_obj

        if os.path.exists(ruta_obj) and ruta_obj.endswith(".obj"):
            # Si el archivo existe, cargar el modelo 3D
            bpy.ops.wm.obj_import(filepath=ruta_obj)
            print("CARGA")
            esfera = bpy.context.selected_objects[0]
            factor_escala = generar_ciudad.tam_calle * 3 
            esfera.scale *= factor_escala

            # Asegúrate de aplicar la escala para solidificar los cambios
            bpy.context.view_layer.objects.active = esfera
            # Selecciona el objeto importado
            bpy.ops.object.transform_apply(
                location=False, rotation=False, scale=True)
            print("Modelo 3D cargado correctamente.")
        else:
            print("No se encontró un modelo .obj válido. Generando esferas por defecto.")
            generar_coches = False  # Revertir a esferas si no hay modelo válido

        if not generar_coches:
            # Crear una esfera en lugar de un coche
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                                 enter_editmode=False,
                                                 align='WORLD',
                                                 # Posición inicial
                                                 location=(
                                                     pos_esfera_x, 0, altura),
                                                 scale=(1, 1, 1))
            esfera = bpy.context.active_object

            # Redimensionar la esfera
            bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                     orient_type='GLOBAL',
                                     orient_matrix=(
                                         (1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                     orient_matrix_type='GLOBAL',
                                     mirror=False,
                                     use_proportional_edit=False,
                                     proportional_edit_falloff='SMOOTH',
                                     proportional_size=1,
                                     use_proportional_connected=False,
                                     use_proportional_projected=False,
                                     snap=False)

            # Añadir el modificador de Subdivision Surface
            mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
            mod.levels = 2  # Nivel de subdivisión en la vista
            mod.render_levels = 3  # Nivel de subdivisión en el render

        # Aplicar el modificador
            bpy.ops.object.modifier_apply(modifier="Subdivision")

        posiciones = crea_ruta(nturns, generar_ciudad.numero_calles_x)
        # Insertar fotogramas clave en cada posición de posns
        for index, pos in enumerate(posiciones):
            # Calcular el frame para cada punto en la ruta
            frame = 1 + int(index * tiempo_por_calle)
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (
                # Configurar la posición de la esfera en el punto actual
                generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)

            # Insertar fotograma clave para la posición
            esfera.keyframe_insert(data_path="location", index=-1)

        bpy.context.view_layer.objects.active = esfera
        bpy.ops.object.create_trayectoria()  # Llama al operador

    elif direccion == 1:
        calle_y = random.randint(0, generar_ciudad.numero_calles_y)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_y = -2 + (calle_y * generar_ciudad.tam_calle) + \
            (calle_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = -2 + (generar_ciudad.numero_calles_x * generar_ciudad.tam_calle) + (
            generar_ciudad.numero_calles_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        if generar_coches:
            print("RUTA OBJETO CARGADA")
            ruta_obj = ruta_completa  # bpy.context.scene.ruta_modelo_obj

        if os.path.exists(ruta_obj) and ruta_obj.endswith(".obj"):
            # Si el archivo existe, cargar el modelo 3D
            bpy.ops.wm.obj_import(filepath=ruta_obj)
            print("CARGA")
            esfera = bpy.context.selected_objects[0]
            factor_escala = generar_ciudad.tam_calle * 3 
            esfera.scale *= factor_escala

            # Asegúrate de aplicar la escala para solidificar los cambios
            bpy.context.view_layer.objects.active = esfera
            # Selecciona el objeto importado
            bpy.ops.object.transform_apply(
                location=False, rotation=False, scale=True)
            print("Modelo 3D cargado correctamente.")
        else:
            print("No se encontró un modelo .obj válido. Generando esferas por defecto.")
            generar_coches = False  # Revertir a esferas si no hay modelo válido

        if not generar_coches:
            # Crear una esfera en lugar de un coche
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                                 enter_editmode=False,
                                                 align='WORLD',
                                                 # Posición inicial
                                                 location=(
                                                     pos_esfera_x, 0, altura),
                                                 scale=(1, 1, 1))
            esfera = bpy.context.active_object

            # Redimensionar la esfera
            bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                     orient_type='GLOBAL',
                                     orient_matrix=(
                                         (1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                     orient_matrix_type='GLOBAL',
                                     mirror=False,
                                     use_proportional_edit=False,
                                     proportional_edit_falloff='SMOOTH',
                                     proportional_size=1,
                                     use_proportional_connected=False,
                                     use_proportional_projected=False,
                                     snap=False)

            # Añadir el modificador de Subdivision Surface
            mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
            mod.levels = 2  # Nivel de subdivisión en la vista
            mod.render_levels = 3  # Nivel de subdivisión en el render

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        # Insertar fotogramas clave en cada posición de posns
        posiciones = crea_ruta(nturns, generar_ciudad.numero_calles_x)
        for index, pos in enumerate(posiciones):
            # Calcular el frame para cada punto en la ruta
            frame = 1 + int(index * tiempo_por_calle)
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (
                # Configurar la posición de la esfera en el punto actual
                generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)

            # Insertar fotograma clave para la posición
            esfera.keyframe_insert(data_path="location", index=-1)

        bpy.context.view_layer.objects.active = esfera
        bpy.ops.object.create_trayectoria()  # Llama al operador

    # O-E
    elif direccion == 2:
        calle_y = random.randint(0, generar_ciudad.numero_calles_y)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_y = -2 + (calle_y * generar_ciudad.tam_calle) + \
            (calle_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = (generar_ciudad.numero_calles_x * generar_ciudad.tam_calle) + (
            generar_ciudad.numero_calles_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        # Crear esfera
        if generar_coches:
            print("RUTA OBJETO CARGADA")
            ruta_obj = ruta_completa  # bpy.context.scene.ruta_modelo_obj

        if os.path.exists(ruta_obj) and ruta_obj.endswith(".obj"):
            # Si el archivo existe, cargar el modelo 3D
            bpy.ops.wm.obj_import(filepath=ruta_obj)
            print("CARGA")
            esfera = bpy.context.selected_objects[0]
            factor_escala = generar_ciudad.tam_calle * 3 
            # Multiplica las dimensiones actuales por el factor de escala
            esfera.scale *= factor_escala

            # Asegúrate de aplicar la escala para solidificar los cambios
            bpy.context.view_layer.objects.active = esfera
            # Selecciona el objeto importado
            bpy.ops.object.transform_apply(
                location=False, rotation=False, scale=True)
            print("Modelo 3D cargado correctamente.")
        else:
            print("No se encontró un modelo .obj válido. Generando esferas por defecto.")
            generar_coches = False  # Revertir a esferas si no hay modelo válido

        if not generar_coches:
            # Crear una esfera en lugar de un coche
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                                 enter_editmode=False,
                                                 align='WORLD',
                                                 # Posición inicial
                                                 location=(
                                                     pos_esfera_x, 0, altura),
                                                 scale=(1, 1, 1))
            esfera = bpy.context.active_object

            # Redimensionar la esfera
            bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                     orient_type='GLOBAL',
                                     orient_matrix=(
                                         (1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                     orient_matrix_type='GLOBAL',
                                     mirror=False,
                                     use_proportional_edit=False,
                                     proportional_edit_falloff='SMOOTH',
                                     proportional_size=1,
                                     use_proportional_connected=False,
                                     use_proportional_projected=False,
                                     snap=False)

            # Añadir el modificador de Subdivision Surface
            mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
            mod.levels = 2  # Nivel de subdivisión en la vista
            mod.render_levels = 3  # Nivel de subdivisión en el render

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")

        # Establecer el frame a 50 y agregar el fotograma clave al final de la calle
       # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        posiciones = crea_ruta(nturns, generar_ciudad.numero_calles_x)
        # Insertar fotogramas clave en cada posición de posns
        for index, pos in enumerate(posiciones):
            # Calcular el frame para cada punto en la ruta
            frame = 1 + int(index * tiempo_por_calle)
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (
                # Configurar la posición de la esfera en el punto actual
                generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)

            # Insertar fotograma clave para la posición
            esfera.keyframe_insert(data_path="location", index=-1)

        bpy.context.view_layer.objects.active = esfera
        bpy.ops.object.create_trayectoria()  # Llama al operador

    elif direccion == 3:
        calle_x = random.randint(0, generar_ciudad.numero_calles_x)

        # Calcular la posición de la esfera entre dos valores consecutivos de X
        pos_esfera_x = -2 + (calle_x * generar_ciudad.tam_calle) + \
            (calle_x * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)
        pos_esfera_fin = -2 + (generar_ciudad.numero_calles_y * generar_ciudad.tam_calle) + (
            generar_ciudad.numero_calles_y * generar_ciudad.tam_edif) + (generar_ciudad.tam_calle / 2)

        altura = random.uniform(5, 15)

        if generar_coches:
            print("RUTA OBJETO CARGADA")
            ruta_obj = ruta_completa  # bpy.context.scene.ruta_modelo_obj

        if os.path.exists(ruta_obj) and ruta_obj.endswith(".obj"):
            # Si el archivo existe, cargar el modelo 3D
            bpy.ops.wm.obj_import(filepath=ruta_obj)
            print("CARGA")
            esfera = bpy.context.selected_objects[0]
            factor_escala = generar_ciudad.tam_calle * 3 
            # Multiplica las dimensiones actuales por el factor de escala
            esfera.scale *= factor_escala

            # Asegúrate de aplicar la escala para solidificar los cambios
            bpy.context.view_layer.objects.active = esfera
            # Selecciona el objeto importado
            bpy.ops.object.transform_apply(
                location=False, rotation=False, scale=True)
            print("Modelo 3D cargado correctamente.")
        else:
            print("No se encontró un modelo .obj válido. Generando esferas por defecto.")
            generar_coches = False  # Revertir a esferas si no hay modelo válido

        if not generar_coches:
            # Crear una esfera en lugar de un coche
            bpy.ops.mesh.primitive_uv_sphere_add(radius=1,
                                                 enter_editmode=False,
                                                 align='WORLD',
                                                 # Posición inicial
                                                 location=(
                                                     pos_esfera_x, 0, altura),
                                                 scale=(1, 1, 1))
            esfera = bpy.context.active_object

            # Redimensionar la esfera
            bpy.ops.transform.resize(value=(generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75, generar_ciudad.tam_calle * 0.75),
                                     orient_type='GLOBAL',
                                     orient_matrix=(
                                         (1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                     orient_matrix_type='GLOBAL',
                                     mirror=False,
                                     use_proportional_edit=False,
                                     proportional_edit_falloff='SMOOTH',
                                     proportional_size=1,
                                     use_proportional_connected=False,
                                     use_proportional_projected=False,
                                     snap=False)

            # Añadir el modificador de Subdivision Surface
            mod = esfera.modifiers.new(name="Subdivision", type='SUBSURF')
            mod.levels = 2  # Nivel de subdivisión en la vista
            mod.render_levels = 3  # Nivel de subdivisión en el render

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")

        # Aplicar el modificador
        bpy.ops.object.modifier_apply(modifier="Subdivision")
        posiciones = crea_ruta(nturns, generar_ciudad.numero_calles_x)
        # Insertar fotogramas clave en cada posición de posns
        for index, pos in enumerate(posiciones):
            # Calcular el frame para cada punto en la ruta
            frame = 1 + int(index * tiempo_por_calle)
            bpy.context.scene.frame_set(frame)
            esfera.location = (pos[0] * (generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, pos[1] * (
                # Configurar la posición de la esfera en el punto actual
                generar_ciudad.tam_calle + generar_ciudad.tam_edif) - generar_ciudad.tam_calle/2, altura)

            # Insertar fotograma clave para la posición
            esfera.keyframe_insert(data_path="location", index=-1)

        # bpy.context.view_layer.objects.active = objeto
        bpy.context.view_layer.objects.active = esfera
        bpy.ops.object.create_trayectoria()  # Llama al operador


class OBJECT_OT_Crear_Mov_Esfera(bpy.types.Operator):
    """
    Operador para crear esferas y asignarles movimientos según parámetros definidos.

    Propósito:
    ----------
    Este operador permite crear un número determinado de esferas en la escena y configurar sus movimientos
    según la velocidad y el número de giros definidos por el usuario en las propiedades de la escena.

    Atributos:
    ----------
    - `bl_idname` : str
        Identificador único del operador. Se usa para invocarlo en scripts y desde la interfaz.
        En este caso: "object.crear_mov_esfera".
    - `bl_label` : str
        Nombre visible del operador en la interfaz.
        En este caso: "Crear Trayectoria".

    Propiedades:
    ------------
    No se definen propiedades dentro de la clase directamente, pero el operador accede a varias
    propiedades de la escena para determinar el comportamiento (como `ruta_modelo_obj`, `velocidad_esfera`, 
    `num_esferas`, y `nturns`).

    Métodos:
    --------
    1. `invoke(self, context, event)`:
        Método invocado cuando se utiliza el operador desde la interfaz. Obtiene las propiedades de la escena,
        y luego llama a la función `CrearEsferas` para generar las esferas en la escena.

        Retorna:
        --------
        - {'FINISHED'}: Indica que el operador se ejecutó correctamente.

    Notas:
    ------
    - La función `CrearEsferas` es la responsable de generar las esferas y asignarles los movimientos.

    Retorno:
    --------
    Ninguno.
    """
    
    bl_idname = "object.crear_mov_esfera"
    bl_label = "Crear Trayectoria"

    def invoke(self, context, event):

        ruta_obj = bpy.context.scene.ruta_modelo_obj

        velocidad = bpy.context.scene.velocidad_esfera
        num_esferas = bpy.context.scene.num_esferas
        nturns = bpy.context.scene.nturns

        # Crear esferas en un bucle
        for i in range(num_esferas):
            CrearEsferas(velocidad, nturns)
            print(f"Esfera {i+1} creada")

        self.report({'INFO'}, f"{num_esferas} esferas creadas exitosamente")
        return {'FINISHED'}


class OBJECT_OT_Borrar_Esferas(bpy.types.Operator):
    """
    Operador para borrar todas las esferas de la escena.

    Propósito:
    ----------
    Este operador recorre todos los objetos de la escena y elimina aquellos que comienzan con el nombre "Sphere".
    Esto permite borrar rápidamente todas las esferas creadas en la escena.

    Atributos:
    ----------
    - `bl_idname` : str
        Identificador único del operador. Se usa para invocarlo en scripts y desde la interfaz.
        En este caso: "object.borrar_esferas".
    - `bl_label` : str
        Nombre visible del operador en la interfaz.
        En este caso: "Borrar Todas las Esferas".

    Métodos:
    --------
    1. `execute(self, context)`:
        Método ejecutado cuando se activa el operador. Elimina todos los objetos que comienzan con "Sphere" de la escena.

        Retorna:
        --------
        - {'FINISHED'}: Indica que el operador se ejecutó correctamente.

    Retorno:
    --------
    Ninguno.
    """
    bl_idname = "object.borrar_esferas"
    bl_label = "Borrar Todas las Esferas"

    def execute(self, context):
        # Recorrer todos los objetos de la escena y eliminar las esferas
        for obj in bpy.context.scene.objects:
            if obj.name.startswith("Car"):
                bpy.data.objects.remove(obj, do_unlink=True)

        self.report({'INFO'}, "Todas las esferas han sido borradas")
        return {'FINISHED'}

# Panel personalizado para controlar las esferas


class OBJECT_PT_VelocidadEsferaPanel(bpy.types.Panel):
    """
    Panel personalizado para controlar las propiedades de las esferas y su movimiento.

    Propósito:
    ----------
    Este panel permite al usuario configurar las propiedades de las esferas, incluyendo su velocidad, número
    de esferas, número de giros, y si debe aplicarse oscilación aleatoria. También incluye botones para
    crear y borrar las esferas de la escena.

    Atributos:
    ----------
    - `bl_label` : str
        Título del panel.
        En este caso: "Control de Esfera".
    - `bl_idname` : str
        Identificador único del panel.
        En este caso: "OBJECT_PT_velocidad_esfera_panel".
    - `bl_space_type` : str
        Tipo de espacio donde se mostrará el panel. En este caso, en la vista 3D.
    - `bl_region_type` : str
        Tipo de región donde se mostrará el panel. En este caso, en la interfaz de usuario.
    - `bl_category` : str
        Categoría en la que aparecerá el panel en la barra lateral de la vista 3D.

    Métodos:
    --------
    1. `draw(self, context)`:
        Método encargado de dibujar el panel en la interfaz. Añade controles para ajustar las propiedades de las esferas
        y otros parámetros relacionados con la ciudad y la rotación.

        Retorna:
        --------
        Ninguno.

    Retorno:
    --------
    Ninguno.
    """
    bl_label = "Control de Esfera"
    bl_idname = "OBJECT_PT_velocidad_esfera_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Control de Esfera"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        # Configuración de la ciudad
        layout.label(text="Configuración de la Ciudad")
        layout.prop(scene, "numero_calles_x_y", text="Número de Calles")
        layout.prop(scene, "amplitud_calle", text="Amplitud de calle")
        layout.operator("object.aplicar_configuracion_ciudad",
                        text="Aplicar Configuración de Ciudad")

        # Control de las esferas existente
        layout.label(text="Controlador de las Esferas")
        layout.prop(scene, "velocidad_esfera", text="Velocidad")
        layout.prop(scene, "num_esferas", text="Número de Esferas")
        layout.prop(scene, "nturns", text="Número de Giros")
        layout.prop(scene, "apply_random_oscillation",
                    text="Oscilación Aleatoria")

        if scene.apply_random_oscillation:
            layout.prop(scene, "oscillation_axes", text="Ejes")
            layout.prop(scene, "oscillation_amplitude", text="Amplitud")
            layout.prop(scene, "oscillation_frequency", text="Frecuencia")

        layout.label(text="Opciones de Generación")
        layout.prop(scene, "generar_coches", text="Generar Coches")
        if scene.generar_coches:  # Mostrar el selector de archivo solo si está activado
            layout.prop(scene, "ruta_modelo_obj", text="Ruta del Modelo")

        layout.operator("object.borrar_esferas", text="Borrar todos los objetos")
        layout.operator("object.crear_mov_esfera", text="Crear coches")

# Operador para aplicar la configuración de la ciudad


class OBJECT_OT_AplicarConfiguracionCiudad(bpy.types.Operator):
    """
    Operador para aplicar la configuración de la ciudad.

    Propósito:
    ----------
    Este operador aplica la configuración de la ciudad llamando a la función `aplicar_configuracion_ciudad`.
    Esto actualiza la escena con los nuevos parámetros de la ciudad y genera los elementos correspondientes.

    Atributos:
    ----------
    - `bl_idname` : str
        Identificador único del operador. Se usa para invocarlo en scripts y desde la interfaz.
        En este caso: "object.aplicar_configuracion_ciudad".
    - `bl_label` : str
        Nombre visible del operador en la interfaz.
        En este caso: "Aplicar Configuración de Ciudad".

    Métodos:
    --------
    1. `execute(self, context)`:
        Método ejecutado cuando se activa el operador. Llama a la función `aplicar_configuracion_ciudad` para aplicar
        los cambios de la ciudad en la escena.

        Retorna:
        --------
        - {'FINISHED'}: Indica que el operador se ejecutó correctamente.

    Retorno:
    --------
    Ninguno.
    """
    bl_idname = "object.aplicar_configuracion_ciudad"
    bl_label = "Aplicar Configuración de Ciudad"

    def execute(self, context):
        aplicar_configuracion_ciudad()
        self.report({'INFO'}, "Ciudad configurada con éxito")
        return {'FINISHED'}


class OBJECT_OT_Quaternion(bpy.types.Operator):
    """
    Operador para calcular y asignar un quaternion de rotación a un objeto.

    Propósito:
    ----------
    Este operador se utiliza para calcular el quaternion de rotación de un objeto seleccionado en la escena y
    asignarlo mediante la función `asigna_drivers_rotacion`, que probablemente ajusta los drivers de rotación
    en función de algún tipo de cálculo o configuración previa.

    Atributos:
    ----------
    - `bl_idname` : str
        Identificador único del operador. Se usa para invocarlo en scripts y desde la interfaz.
        En este caso: "object.calcular_quaternion".
    - `bl_label` : str
        Nombre visible del operador en la interfaz.
        En este caso: "Calcular quaternion".

    Métodos:
    --------
    1. `execute(self, context)`:
        Método ejecutado cuando se activa el operador. Obtiene el objeto activo en la escena y llama a la función
        `posicion.asigna_drivers_rotacion` para asignar el quaternion de rotación al objeto.

        Retorna:
        --------
        - {'FINISHED'}: Indica que el operador se ejecutó correctamente.

    Notas:
    ------
    - La función `asigna_drivers_rotacion` es probablemente responsable de aplicar un conjunto de drivers de
      rotación al objeto, ajustando su orientación de acuerdo con la lógica definida.

    Retorno:
    --------
    Ninguno.
    """
    bl_idname = "object.calcular_quaternion"
    bl_label = "Calcular quaternion"

    def execute(self, context):
        obj = context.object

        # for obj in bpy.context.scene.objects:
        # if obj.name.startswith("Sphere"):
        posicion.asigna_drivers_rotacion(obj)
        self.report({'INFO'}, "Quaternion OK")
        return {'FINISHED'}


def verificar_fcurves(obj):
    if not obj.animation_data or not obj.animation_data.action:
        print("El objeto no tiene datos de animación o acción activa.")
        return

    fcurves = obj.animation_data.action.fcurves
    for fcurve in fcurves:
        print("F-curve data path:", fcurve.data_path,
              "Index:", fcurve.array_index)


def register():
    # Registra solo las clases específicas de __init__.py
    bpy.utils.register_class(OBJECT_PT_VelocidadEsferaPanel)
    bpy.utils.register_class(OBJECT_OT_Crear_Mov_Esfera)
    bpy.utils.register_class(OBJECT_OT_Borrar_Esferas)
    bpy.utils.register_class(OBJECT_OT_AplicarConfiguracionCiudad)
    bpy.utils.register_class(OBJECT_OT_Quaternion)

    # Registra el módulo posicion
    posicion.register()


def unregister():
    # Desregistra clases específicas de __init__.py
    try:
        bpy.utils.unregister_class(OBJECT_PT_VelocidadEsferaPanel)
    except RuntimeError:
        pass
    try:
        bpy.utils.unregister_class(OBJECT_OT_AplicarConfiguracionCiudad)
    except RuntimeError:
        pass
    try:
        bpy.utils.unregister_class(OBJECT_OT_Crear_Mov_Esfera)
    except RuntimeError:
        pass

    try:
        bpy.utils.unregister_class(OBJECT_OT_Borrar_Esferas)
    except RuntimeError:
        pass
    try:
        bpy.utils.unregister_class(OBJECT_OT_Quaternion)
    except RuntimeError:
        pass

    try:
        posicion.unregister()
    except RuntimeError:
        pass


if __name__ == "__main__":
    unregister()
    register()
