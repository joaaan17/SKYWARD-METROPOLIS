import bpy
import math
import mathutils
import sys
import os
# import interpola
import importlib

from bpy.props import FloatVectorProperty
from mathutils import noise

try:
    import interpola
    importlib.reload(interpola)
except ImportError:
    import posiciinterpolaon

# Añadir la ruta donde se encuentran tus módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

eje_items = [
    ('X', 'X', 'Alinear con el eje X'),
    ('Y', 'Y', 'Alinear con el eje Y'),
    ('Z', 'Z', 'Alinear con el eje Z'),
    ('-X', '-X', 'Alinear con el eje -X'),
    ('-Y', '-Y', 'Alinear con el eje -Y'),
    ('-Z', '-Z', 'Alinear con el eje -Z')
]

bpy.types.Object.eje_alineacion = bpy.props.EnumProperty(
    name="Eje de Alineación",
    description="Selecciona el eje del objeto que se alineará con el vector tangente",
    items=eje_items,
    default='Y'  # Puedes cambiar el valor predeterminado
)

bpy.types.Object.eje_arriba = bpy.props.EnumProperty(
    name="Eje de arriba ",
    description="Selecciona el eje del objeto que se alineará con el vector up",
    items=eje_items,
    default='Z'  # Puedes cambiar el valor predeterminado
)

bpy.types.Object.angulo_rotacion = bpy.props.FloatProperty(
    name="Angulo de giro",
    description="Selecciona angulo que girará el objeto al tomar una curva",
    default=0,
    min=-90,
    max=90,
    unit='ROTATION'
)

bpy.types.Scene.tension = bpy.props.FloatProperty(
    name="Tension",
    description="Tensión para Catmull-Rom",
    default=0.5,
    min=0.0  # Sin límite superior
)

enum_items = [
    ('LINEAL', "Interpolacion lineal", "Interpola linealmente"),
    ('CATMULL-ROM', "Interpolacion Catmull-Rom", "Interpola usando Catmull-Rom"),
    ('HERMITE', "Interpolacion Hermite", "Interpola usando Hermite")
]

bpy.types.Scene.selected_shape = bpy.props.EnumProperty(
    name="Tipo de interpolación",
    description="Selecciona la interpolación",
    items=enum_items,
    default='LINEAL'
)

bpy.types.Object.velocity = FloatVectorProperty(
    name="Velocity",
    description="Velocidad en el keyframe como un vector 3D",
    default=(0.0, 0.0, 0.0),  # Valor por defecto si no se especifica
    size=3  # Tamaño del vector (x, y, z)
)

bpy.types.Object.distancia_deseada = bpy.props.FloatProperty(
    name="Distancia Deseada",
    description="Distancia que se desea recorrer a lo largo de la curva",
    default=0.0,
    min=0.0,
)

bpy.types.Object.distancia_recorrida = bpy.props.FloatProperty(
    name="Longitud recorrida",
    description="longitud recorrida por el objeto",
    default=0.0,
    min=0.0,
)

bpy.types.Object.control_vel = bpy.props.BoolProperty(
    name="Aplicar control de velocidad",
    description="Activar o desactivar contorl de velocidad",
    default=False
)


def get_random_oscillation(frame, frequency, amplitude, axes):
    """
    Parámetros:
    ----------
    frame : int
        El frame actual en el que se calculará la oscilación. Esto permite que la
        oscilación sea dependiente del tiempo o de la animación.

    frequency : float
        La frecuencia de la oscilación. Valores más altos generarán oscilaciones más rápidas
        (mayor densidad en el ruido generado).

    amplitude : float
        La amplitud de la oscilación. Esto escala los valores de ruido, determinando
        la intensidad máxima del desplazamiento generado.

    axes : list[str]
        Una lista de ejes ('X', 'Y', 'Z') en los que se aplicará la oscilación. Por ejemplo,
        si se pasa `['X', 'Z']`, la oscilación solo afectará a los ejes X y Z.

    Retorno:
    -------
    osc_values : dict[str, float]    
    """

    t = frame * frequency
    osc_values = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}

    # Genera el valor de ruido para cada eje especificado en `axes`
    if 'X' in axes:
        osc_values['X'] = amplitude * \
            noise.noise([t, 0.0, 0.0])  # Ruido en el eje X
    if 'Y' in axes:
        osc_values['Y'] = amplitude * \
            noise.noise([0.0, t, 0.0])  # Ruido en el eje Y
    if 'Z' in axes:
        osc_values['Z'] = amplitude * \
            noise.noise([0.0, 0.0, t])  # Ruido en el eje Z

    return osc_values


def get_posicion_x_loop(frame):
    '''
    Calcula la posición en el eje X de un movimiento circular centrado en el origen.

    Parámetros:
    ----------
    frame : int
        El frame actual en el que se calcula la posición. Se utiliza para determinar
        la posición angular en el círculo.

    Retorno:
    -------
    float
        La posición en el eje X correspondiente al frame dado.
    '''
    t = frame / 24.0
    return 5 * math.cos(t)  # Radio de 5, centrado en el origen


def get_posicion_y_loop(frame):
    '''
    Calcula la posición en el eje Y de un movimiento circular centrado en el origen.

    Parámetros:
    ----------
    frame : int
        El frame actual en el que se calcula la posición. Se utiliza para determinar
        la posición angular en el círculo.

    Retorno:
    -------
    float
        La posición en el eje Y correspondiente al frame dado.
    '''
    t = frame / 24.0
    return 5 * math.sin(t)  # Radio de 5, centrado en el origen


def get_posicion1(frm: float):
    '''
    Calcula una posición en el eje X basada en un movimiento lineal segmentado.

    Este movimiento tiene tres fases:
    - Para `t <= 0`: la posición es 0.
    - Para `0 < t <= 5`: la posición aumenta linealmente de 0 a 10.
    - Para `t > 5`: la posición se mantiene constante en 10.

    Parámetros:
    ----------
    frm : float
        El número de frame en el que se evalúa la posición.

    Retorno:
    -------
    float
        La posición calculada en el eje X para el frame dado.
    '''
    t = frm / 24.0
    if t <= 0:
        posx = 0.0
    elif t <= 5.0:
        posx = 10.0 * t / 5.0
    else:
        posx = 10.0
    print(f"Frame: {frm}, Posición X: {posx}")
    return posx


def get_posicion2(frm, obj, coord):
    '''
    Obtiene la posición interpolada de un objeto en un eje específico en un frame determinado.

    Esta función evalúa la posición de un objeto en función de las curvas de animación (fCurves) 
    y aplica diferentes métodos de interpolación, además de oscilaciones aleatorias si están habilitadas.

    Parámetros:
    ----------
    frm : int
        El número del frame actual.
    obj : bpy.types.Object
        El objeto para el cual se desea calcular la posición.
    coord : int
        El índice de la coordenada (0 para X, 1 para Y, 2 para Z).

    Retorno:
    -------
    float
        La posición calculada para el objeto en el eje especificado.

    Métodos de interpolación:
    -------------------------
    - LINEAL: Interpolación lineal entre keyframes.
    - CATMULL-ROM: Interpolación basada en el método Catmull-Rom con soporte para tensiones ajustables.
    - HERMITE: Interpolación Hermite que utiliza velocidades evaluadas en los keyframes.
    '''

    # Obtiene la curva de animación
    c = obj.animation_data.action.fcurves.find('location', index=coord)

    if not c:
        print("Curva de animación no encontrada.")
        return 0.0

    # Si hay menos de dos keyframes, devolver la posición del único keyframe
    if len(c.keyframe_points) == 1:
        return c.keyframe_points[0].co[1]

    frm = change_frame(obj, frm)
    # print("Nuevo FRAME -->", frm)
    # Si el frame es menor que el primer keyframe, devolver el valor del primer keyframe
    if frm < c.keyframe_points[0].co[0]:
        # print("El frame está antes del primer keyframe.")
        return c.keyframe_points[0].co[1]

    # Si el frame es mayor que el último keyframe, devolver el valor del último keyframe
    if frm > c.keyframe_points[-1].co[0]:
        # print("El frame está después del último keyframe.")
        return c.keyframe_points[-1].co[1]

    prev_kf = None
    next_kf = None

    # Encontrar los dos keyframes entre los que se encuentra el frame actual
    for i in range(len(c.keyframe_points) - 1):
        kf1 = c.keyframe_points[i]
        kf2 = c.keyframe_points[i + 1]

        if kf1.co[0] <= frm <= kf2.co[0]:
            anterior_kf = c.keyframe_points[i - 1] if i > 0 else None
            prev_kf = kf1
            next_kf = kf2
            posterior_kf = c.keyframe_points[i + 2] if i + \
                2 < len(c.keyframe_points) else None
            break

    # Manejo de casos fuera de los keyframes
    if prev_kf is None or next_kf is None:
        print("El frame está fuera de los keyframes")
        return None  # Retornar None si el frame está fuera de los keyframes

    # Dependiendo del método de interpolación seleccionado, se elige el algoritmo
    selected_interpolation = bpy.context.scene.selected_shape

    if selected_interpolation == 'LINEAL':
        pos = interpola.lineal(
            frm, prev_kf.co[0], next_kf.co[0], prev_kf.co[1], next_kf.co[1])

    elif selected_interpolation == 'CATMULL-ROM':
        tension = bpy.context.scene.tension  # Obtener la tensión desde el panel

        if len(c.keyframe_points) >= 2:
            # Estos pueden ser keyframes anteriores y siguientes a los actuales
            p0 = anterior_kf.co[1] if anterior_kf is not None else prev_kf.co[1]
            p1 = prev_kf.co[1]
            p2 = next_kf.co[1]
            p3 = posterior_kf.co[1] if posterior_kf is not None else next_kf.co[1]

            # Lo mismo con los tiempos
            t0 = anterior_kf.co[0] if anterior_kf is not None else prev_kf.co[0]
            t1 = prev_kf.co[0]
            t2 = next_kf.co[0]
            t3 = posterior_kf.co[0] if posterior_kf is not None else next_kf.co[0]

            # Realizar la interpolación
            pos = interpola.catmull_rom(
                frm, t0, t1, t2, t3, p0, p1, p2, p3, tension)
            # print("NUEVA POS -->", pos)

    elif selected_interpolation == 'HERMITE':
        # Buscar la fCurve de velocidad del objeto
        velocity_fcurve = None
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                if fcurve.data_path == 'velocity':
                    velocity_fcurve =  obj.animation_data.action.fcurves.find('velocity', index=coord)
                    break

        # Evaluar las velocidades en los keyframes previos y siguientes
        if velocity_fcurve is not None:
            # Evaluar la velocidad en t0
            v0 = velocity_fcurve.evaluate(prev_kf.co[0])
            # Evaluar la velocidad en t1
            v1 = velocity_fcurve.evaluate(next_kf.co[0])
        else:
            v0 = 0.0
            v1 = 0.0

        # Asegurarse de que t0 y t1 no son iguales para evitar división por cero en Hermite
        if prev_kf.co[0] != next_kf.co[0]:
            # Llamar a la función Hermite con las velocidades adecuadas
            pos = interpola.hermite(
                frm,                    # El tiempo del frame actual
                prev_kf.co[0],          # t0: tiempo del keyframe previo
                next_kf.co[0],          # t1: tiempo del keyframe siguiente
                prev_kf.co[1],          # p0: valor en el keyframe previo
                next_kf.co[1],          # p1: valor en el keyframe siguiente
                # v0 ajustado al intervalo de tiempo entre t0 y t1
                v0 * (next_kf.co[0] - prev_kf.co[0]),
                # v1 ajustado al intervalo de tiempo entre t0 y t1
                v1 * (next_kf.co[0] - prev_kf.co[0])
            )

        else:
            # Si t0 y t1 son iguales, devuelve el valor del keyframe sin interpolación
            pos = prev_kf.co[1]

     # Obtener los valores de las propiedades de oscilación
    frecuencia = bpy.context.scene.oscillation_frequency
    amplitud = bpy.context.scene.oscillation_amplitude
    axis = bpy.context.scene.oscillation_axes

    osc_values = get_random_oscillation(frm, frecuencia, amplitud, axis)
    if coord == 0:  # Eje X
        pos += osc_values['X']
    elif coord == 1:  # Eje Y
        pos += osc_values['Y']
    elif coord == 2:  # Eje Z
        pos += osc_values['Z']

    return pos


def change_frame(obj, frm):
    """
    Ajusta el fotograma en función de la distancia deseada y la reparametrización de la curva.

    Parámetros:
    obj -- El objeto animado que contiene las propiedades y datos de animación.
    frm -- El fotograma actual que se está evaluando.

    Retorna:
    frm -- El fotograma ajustado según la longitud deseada.
    """
    long = 0

    if obj.control_vel:

        fc = obj.animation_data.action.fcurves.find("distancia_deseada")
        print("CAMBIANDO FRAME -->", frm)

        if fc is None:
            long = 0
        else:
            long = fc.evaluate(frm)

        frm = frame_desde_longitud(obj, long)

    return frm


def frame_desde_longitud(obj, long):
    fcLongRec = obj.animation_data.action.fcurves.find("distancia_recorrida")

    if not fcLongRec:
        print("Fcurve no encontrada")
        return None

    # Utilizar los rangos de frame de la escena
    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    last_value = None
    last_frame = None

    for frm in range(frame_start, frame_end + 1):
        current_value = fcLongRec.evaluate(frm)

        if current_value == long:
            print("FRAME -->", frm, "LONGITUD -->", long)
            return frm

        if last_value is not None and ((last_value < long and current_value > long) or (last_value > long and current_value < long)):
            # f(x) = x0 + (x - y0) * ((x1 - x0) / (y1 - y0))
            # Aquí, long es t, last_value es y0, current_value es y1, last_frame es t0 y frm es t1
            frm_interpolado = last_frame + \
                ((long - last_value) * (frm - last_frame) /
                 (current_value - last_value))
            print("FRAME interpolado -->", frm_interpolado, "LONGITUD -->", long)
            return frm_interpolado

        last_value = current_value
        last_frame = frm

    print("No se pudo encontrar un frame adecuado para la longitud dada.")
    return last_frame


def longitud_recorrida(obj):
    """
    Calcula la distancia acumulada recorrida por un objeto frame a frame 
    y la almacena en la propiedad `distancia_recorrida` del objeto. 
    Además, inserta keyframes para registrar la distancia acumulada en cada frame.

    Parámetros:
    -----------
    obj : bpy.types.Object
        El objeto animado del que se calcula la distancia acumulada 
        en base a su posición en los ejes X, Y y Z.

    Descripción:
    ------------
    - Este método recorre todos los frames de la animación, desde `frame_start` 
      hasta `frame_end`, y calcula la distancia entre la posición actual y 
      la posición del frame anterior.
    - La distancia acumulada se almacena en la propiedad personalizada 
      `distancia_recorrida` del objeto.
    - Inserta un keyframe en cada frame para la propiedad `distancia_recorrida`, 
      permitiendo visualizar el cambio de esta propiedad en la línea de tiempo.

    Notas:
    ------
    - La propiedad `distancia_recorrida` debe estar previamente registrada 
      como un `FloatProperty` en el objeto.
    - La función utiliza un método auxiliar `get_posicion2` para obtener 
      las posiciones del objeto en los ejes X, Y, Z en un frame dado.

    Retorno:
    --------
    float
        La distancia total acumulada recorrida por el objeto al final 
        de la animación.

    """

    distancia_acumulada = 0.0

    scene = bpy.context.scene
    frame_start = scene.frame_start
    frame_end = scene.frame_end

    pos_anterior_x = pos_anterior_y = pos_anterior_z = None

    for frm in range(frame_start, frame_end + 1):
        pos_actual_x = get_posicion2(frm, obj, 0)
        pos_actual_y = get_posicion2(frm, obj, 1)
        pos_actual_z = get_posicion2(frm, obj, 2)

        if frm == frame_start:
            pos_anterior_x = pos_actual_x
            pos_anterior_y = pos_actual_y
            pos_anterior_z = pos_actual_z

        distancia = math.sqrt(
            (pos_actual_x - pos_anterior_x) ** 2 +
            (pos_actual_y - pos_anterior_y) ** 2 +
            (pos_actual_z - pos_anterior_z) ** 2
        )

        distancia_acumulada += distancia

        obj.distancia_recorrida = distancia_acumulada

        obj.keyframe_insert(data_path="distancia_recorrida", frame=frm)

        pos_anterior_x = pos_actual_x
        pos_anterior_y = pos_actual_y
        pos_anterior_z = pos_actual_z

        print(
            f"FRAME --> {frm}, DISTANCIA ACUMULADA --> {distancia_acumulada}")

    return distancia_acumulada


def get_lat_vec(t):
    '''
    Calcula el vector lateral (perpendicular al vector `t` y al eje Z global).

        Parámetros:
        ----------
        t : mathutils.Vector
            El vector tangente (dirección principal del movimiento o trayectoria).

        Retorno:
        -------
        mathutils.Vector
            El vector lateral calculado.
    '''
    z = mathutils.Vector((0, 0, 1))
    l = z.cross(t)
    l = l.normalized()

    return l


def get_up_vec(t, l):
    '''
    Calcula el vector "up" (arriba) para un sistema de coordenadas basado en `t` y `l`.

    Este vector es perpendicular tanto al vector tangente (`t`) como al vector lateral (`l`).

    Parámetros:
    ----------
    t : mathutils.Vector
        El vector tangente (dirección principal del movimiento o trayectoria).
    l : mathutils.Vector
        El vector lateral (perpendicular al vector tangente y al eje Z global).

    Retorno:
    -------
    mathutils.Vector
        El vector "up" (arriba) calculado.
    '''
    up = t.cross(l)
    up = up.normalized()

    if up.z < 0:
        up = -up

    return up


def get_quad_from_vecs(e, t):
    '''
    Calcula el cuaternión que representa la rotación necesaria para alinear dos vectores.

    Parámetros:
    ----------
    e : mathutils.Vector
        El vector inicial que se desea alinear.
    t : mathutils.Vector
        El vector objetivo al que se desea alinear.

    Retorno:
    -------
    mathutils.Quaternion
        Un cuaternión que representa la rotación necesaria para alinear `e` con `t`.

    Descripción:
    ------------
    Esta función calcula un cuaternión que rota el vector `e` para alinearlo con el vector `t`.
    Maneja los casos especiales en los que los vectores son iguales, opuestos o tienen longitud cero.

    '''
    e = e.normalized()
    t = t.normalized()

    if e.length == 0 or t.length == 0:
        print("Error: Uno de los vectores tiene longitud cero.")
        return mathutils.Quaternion((1, 0, 0, 0))  # Cuaternión identidad

    if e == t:
        return mathutils.Quaternion((1, 0, 0, 0))  # Rotación de 0 grados

    if e == -t:
        axis = e.orthogonal().normalized()
        # Rotación de 180 grados
        return mathutils.Quaternion(axis, 3.141592653589793)

    # Eje de rotación
    v = e.cross(t).normalized()

    # Ángulo de rotación
    angle = e.angle(t)

    # Construir el cuaternión
    q = mathutils.Quaternion(v, angle)

    return q


def get_quat_rot(e, t, up, angle_q3, angle_gir, obj):
    '''
    Calcula el cuaternión que representa la rotación total de un objeto para alinearlo y aplicar inclinación lateral en curvas.

    Parámetros:
    ----------
    e : mathutils.Vector
        Vector inicial que representa el eje del objeto que se desea alinear.
    t : mathutils.Vector
        Vector objetivo o tangente de la trayectoria.
    up : mathutils.Vector
        Vector "arriba" que define la orientación deseada del objeto.
    angle_q3 : float
        Ángulo adicional de rotación lateral que se aplica en curvas.
    angle_gir : float
        Ángulo de giro entre el vector director actual y el anterior en la trayectoria.
    obj : bpy.types.Object
        Objeto de Blender que contiene la propiedad `eje_arriba`, usada para definir el eje local que se alinea con el vector `up`.

    Retorno:
    -------
    mathutils.Quaternion
        Cuaternión que representa la rotación total del objeto.

    Descripción:
    ------------
    Esta función calcula el cuaternión de rotación total para un objeto en Blender, alineando su orientación con la trayectoria y
    aplicando inclinación lateral en las curvas. El cálculo se realiza en tres pasos principales:
    '''
    e = e.normalized()
    t = t.normalized()
    up = up.normalized()

    if obj.eje_arriba == 'X':
        e3 = mathutils.Vector((1, 0, 0))
    elif obj.eje_arriba == 'Y':
        e3 = mathutils.Vector((0, 1, 0))
    elif obj.eje_arriba == 'Z':
        e3 = mathutils.Vector((0, 0, 1))
    elif obj.eje_arriba == '-X':
        e3 = mathutils.Vector((-1, 0, 0))
    elif obj.eje_arriba == '-Y':
        e3 = mathutils.Vector((0, -1, 0))
    elif obj.eje_arriba == '-Z':
        e3 = mathutils.Vector((0, 0, -1))
    # Primer cuaternión: alinear e con t
    q1 = get_quad_from_vecs(e, t)

    e3_rot = q1 @ e3
    e3_rot = e3_rot.normalized()

    q2 = get_quad_from_vecs(e3_rot, up)

    if abs(angle_gir) > 0.00:
        if angle_gir > 0:
            q3 = mathutils.Quaternion(t, angle_q3 * angle_gir)
            return q3 @ q2 @ q1
        elif angle_gir < 0:
            q3 = mathutils.Quaternion(t, -angle_q3 * -angle_gir)
            return q3 @ q2 @ q1
    else:
        return q2 @ q1


def get_quaternion(frm, obj, coord):
    '''
    Calcula el cuaternión de rotación necesario para alinear un objeto a lo largo de una trayectoria interpolada,
    considerando la orientación y posibles inclinaciones laterales.

    Parámetros:
    ----------
    frm : int
        El número de frame actual.
    obj : bpy.types.Object
        El objeto de Blender cuyo cuaternión de rotación se va a calcular.
    coord : int
        Índice de la componente del cuaternión a devolver:
        - 0 para `w`
        - 1 para `x`
        - 2 para `y`
        - 3 para `z`

    Retorno:
    -------
    float
        Componente del cuaternión correspondiente al índice `coord`.

    Descripción:
    ------------
    La función utiliza las posiciones interpoladas del objeto en los frames actual, anterior y siguiente
    para calcular vectores tangentes a la trayectoria. Estos vectores se usan para alinear la orientación
    del objeto y aplicar rotaciones adicionales si es necesario.
    '''
    pos_actual_x = get_posicion2(frm + 1, obj, 0)
    pos_actual_y = get_posicion2(frm + 1, obj, 1)
    pos_actual_z = get_posicion2(frm + 1, obj, 2)

    v_actual = mathutils.Vector((pos_actual_x, pos_actual_y, pos_actual_z))

    pos_anterior_x = get_posicion2(frm, obj, 0)
    pos_anterior_y = get_posicion2(frm, obj, 1)
    pos_anterior_z = get_posicion2(frm, obj, 2)

    v_anterior = mathutils.Vector(
        (pos_anterior_x, pos_anterior_y, pos_anterior_z))

    pos_previa = mathutils.Vector((
        get_posicion2(frm - 1, obj, 0),
        get_posicion2(frm - 1, obj, 1),
        get_posicion2(frm - 1, obj, 2)
    ))

    if v_actual is None or v_anterior is None:
        # print("Error: v_actual o v_anterior es None.")
        return None

    t = calculate_vector_director(v_anterior, v_actual)
    t_anterior = calculate_vector_director(pos_previa, v_anterior)
    if t_anterior.length == 0:
        t_anterior = t

    angle_gir = angle_in_xy_plane(t, t_anterior)

    if t.length == 0:
        # print("VECTOR T tiene longitud 0. Manteniendo la rotación actual.")
        current_rotation = obj.rotation_quaternion
        if coord == 0:
            return current_rotation.w
        elif coord == 1:
            return current_rotation.x
        elif coord == 2:
            return current_rotation.y
        elif coord == 3:
            return current_rotation.z

    e = mathutils.Vector((0, 0, 0))
    if obj.eje_alineacion == 'X':
        e = mathutils.Vector((1, 0, 0))
    elif obj.eje_alineacion == 'Y':
        e = mathutils.Vector((0, 1, 0))
    elif obj.eje_alineacion == 'Z':
        e = mathutils.Vector((0, 0, 1))
    elif obj.eje_alineacion == '-X':
        e = mathutils.Vector((-1, 0, 0))
    elif obj.eje_alineacion == '-Y':
        e = mathutils.Vector((0, -1, 0))
    elif obj.eje_alineacion == '-Z':
        e = mathutils.Vector((0, 0, -1))

    l = get_lat_vec(t)
    up = get_up_vec(t, l)

    angle_q3 = obj.angulo_rotacion

    q_final = get_quat_rot(e, t, up, angle_q3, angle_gir, obj)

    if coord == 0:
        return q_final.w
    elif coord == 1:
        return q_final.x
    elif coord == 2:
        return q_final.y
    elif coord == 3:
        return q_final.z


def angle_in_xy_plane(v1, v2):
    '''
    Calcula el ángulo en el plano XY entre dos vectores dados, considerando la dirección del giro.

    Parámetros:
    ----------
    v1 : mathutils.Vector
        El primer vector en el espacio 3D.
    v2 : mathutils.Vector
        El segundo vector en el espacio 3D.

    Retorno:
    -------
    float
        Ángulo en radianes entre los vectores `v1` y `v2` proyectados sobre el plano XY. El ángulo es positivo
        si el giro es en sentido antihorario y negativo si es en sentido horario.

    Descripción:
    ------------
    La función proyecta los vectores dados sobre el plano XY (ignorando su componente Z) y calcula el ángulo
    entre ellos. Luego, utiliza el producto cruzado para determinar la dirección del ángulo, es decir, si el
    giro es en sentido horario o antihorario.
    '''

    # Proyectar los vectores sobre el plano XY
    v1_proj = mathutils.Vector((v1.x, v1.y, 0))  # Ignorar la componente Z
    v2_proj = mathutils.Vector((v2.x, v2.y, 0))  # Ignorar la componente Z

    if v1_proj.length == 0 or v2_proj.length == 0:
        # print("Advertencia: Uno de los vectores tiene longitud cero.")
        return 0.0  # Devuelve 0 grados como caso especial

    # Normalizar los vectores proyectados para evitar problemas con la longitud
    v1_proj.normalize()
    v2_proj.normalize()

    # Calcular el ángulo entre los vectores proyectados
    angle = v1_proj.angle(v2_proj)

    # Determinar la dirección del ángulo con el producto cruzado
    # Tomar solo la componente Z del producto cruzado
    cross_z = v1_proj.cross(v2_proj).z

    if cross_z < 0:  # Si es negativo, el ángulo es en sentido horario
        angle = -angle

    return angle


def calculate_vector_director(position_current, position_next):
    '''
    Calcula el vector director unitario entre dos posiciones en el espacio 3D.

    Parámetros:
    ----------
    position_current : mathutils.Vector
        El vector de posición actual en el espacio 3D.
    position_next : mathutils.Vector
        El vector de la siguiente posición en el espacio 3D.

    Retorno:
    -------
    mathutils.Vector
        El vector director unitario (normalizado) que apunta desde `position_current` hacia `position_next`.
        Si ambos vectores son iguales, se devuelve un vector nulo (0, 0, 0) con un mensaje de error.

    Descripción:
    ------------
    Esta función calcula el vector director entre dos posiciones en el espacio tridimensional. 
    El vector resultante es normalizado para obtener un vector unitario que conserva únicamente la dirección, 
    eliminando cualquier efecto de la magnitud original.
    '''

    vector_director = position_next - position_current

    if vector_director.length == 0:
        # print("Error: v_anterior y v_acutual son iguales. No se puede calcular un vector director.")
        return mathutils.Vector((0, 0, 0))

    vector_director = vector_director.normalized()

    return vector_director


def sincronizar_keyframes_velocidad(obj):
    '''
    Sincroniza las velocidades del objeto con los keyframes de posición y asigna valores iniciales.

    Parámetros:
    -----------
    obj : bpy.types.Object
        El objeto de Blender al que se le asignarán las velocidades calculadas en función de sus keyframes de posición.

    Retorno:
    --------
    None
        La función no devuelve ningún valor, pero actualiza las velocidades del objeto y añade keyframes de velocidad.

    Descripción:
    ------------
    Esta función calcula las velocidades iniciales del objeto basándose en los keyframes de posición y 
    las sincroniza con una propiedad de velocidad del objeto. Los valores de velocidad se calculan como 
    el cambio de posición dividido entre el tiempo (frames) entre dos keyframes consecutivos.
    '''
    # Comprobar si el objeto tiene datos de animación
    if not obj.animation_data or not obj.animation_data.action:
        print("El objeto no tiene datos de animación.")
        return

    # Recorrer todas las fCurves para encontrar las que son de 'location'
    fcurves_location = [
        fcurve for fcurve in obj.animation_data.action.fcurves if "location" in fcurve.data_path]

    if not fcurves_location:
        print("No se encontraron fCurves de ubicación.")
        return

    # Asumimos que tenemos las fcurves para x, y, z en la lista
    for i, fcurve in enumerate(fcurves_location):
        keyframes = fcurve.keyframe_points

        for k in range(len(keyframes) - 1):
            kf1 = keyframes[k]
            kf2 = keyframes[k + 1]

            frame1 = kf1.co[0]
            frame2 = kf2.co[0]

            pos1 = kf1.co[1]
            pos2 = kf2.co[1]

            # Calcular la velocidad como el cambio de posición dividido por el tiempo entre los keyframes
            tiempo = frame2 - frame1
            if tiempo != 0:
                velocidad = (pos2 - pos1) / tiempo
            else:
                velocidad = 0.0

            # Solo asignar la velocidad inicial al objeto
            obj.velocity[i] = velocidad

            # Insertar un keyframe para la propiedad de velocidad en el frame inicial
            obj.keyframe_insert(data_path="velocity", index=i, frame=frame1)

            # print(f"Keyframe de velocidad insertado en frame {frame1}, velocidad: {velocidad} en coordenada {i}")


def asigna_driver_posicion(obj):
    '''
    Asigna un driver para controlar la posición (location) del objeto en las tres coordenadas (X, Y, Z).

    Parámetros:
    -----------
    obj : bpy.types.Object
        El objeto de Blender al que se le asignarán los drivers de posición.

    Retorno:
    --------
    None
        La función no devuelve ningún valor, pero asigna drivers a las propiedades de posición del objeto.

    Descripción:
    ------------
    Esta función agrega drivers a las propiedades de posición (`location`) del objeto para cada coordenada (X, Y, Z). 
    Los drivers calculan la posición del objeto utilizando una función personalizada (`get_pos2`) que toma como
    entrada el frame actual, el objeto y la coordenada específica.

    '''
    for coord in range(3):
        print("coordenada:", coord)
        drv = obj.driver_add('location', coord).driver
        drv.use_self = True
        drv.expression = f"get_pos2(frame, self, {coord})"

        # Añadir una variable de dependencia para el driver, para que se actualice con selected_shape
        var = drv.variables.new()
        var.name = 'selected_shape'
        var.targets[0].id_type = 'SCENE'
        var.targets[0].id = bpy.context.scene
        var.targets[0].data_path = 'selected_shape'


def asigna_drivers_rotacion(obj):
    '''
    Asigna drivers para controlar la rotación del objeto utilizando cuaterniones.

    Parámetros:
    -----------
    obj : bpy.types.Object
        El objeto de Blender al que se le asignarán los drivers de rotación.

    Descripción:
    ------------
    Esta función agrega drivers a las propiedades de rotación cuaternión (`rotation_quaternion`) del objeto. Los drivers
    permiten calcular dinámicamente la rotación en función de una función personalizada (`get_quaternion`) y los 
    parámetros definidos en la escena.
    '''

    if bpy.context.scene.control_rotacion:
        for coord in range(4):  # 4 componentes: w, x, y, z
            driver = obj.driver_add('rotation_quaternion', coord).driver
            driver.use_self = True
            driver.expression = f"get_quaternion(frame, self, {coord})"

        # Añadir una variable de dependencia para el driver, para que se actualice con selected_shape
        var = driver.variables.new()
        var.name = 'selected_shape'
        var.targets[0].id_type = 'SCENE'
        var.targets[0].id = bpy.context.scene
        var.targets[0].data_path = 'selected_shape'


class OBJECT_PT_CustomPanel(bpy.types.Panel):
    '''
    Panel de control para los drivers en Blender.

    Propósito:
    ----------
    Este panel proporciona una interfaz gráfica en la barra lateral de Blender para gestionar la configuración
    de trayectorias interpoladas y drivers asociados a las animaciones.

    Detalles del panel:
    -------------------
    - **Etiqueta del panel:** "Drivers Control".
    - **Identificador único:** "OBJECT_PT_custom_panel".
    - **Espacio de trabajo:** Vista 3D (`VIEW_3D`).
    - **Región:** UI (Interfaz de usuario).
    - **Categoría:** "Drivers Control".

    Funcionalidad:
    --------------
    1. **Selección de interpolación**:
       - Ofrece un desplegable (`EnumProperty`) para seleccionar la forma de interpolación en la escena.
       - Si se selecciona `CATMULL-ROM`, permite configurar la tensión específica mediante un slider adicional.

    2. **Control de velocidad para HERMITE**:
       - Si la interpolación seleccionada es `HERMITE` y el objeto activo tiene una propiedad `velocity`,
         se muestra un control para configurar la velocidad.

    3. **Configuración de ejes y rotaciones**:
       - Permite ajustar los ejes de alineación (`eje_alineacion`), el eje superior (`eje_arriba`), y el ángulo de rotación (`angulo_rotacion`) del objeto activo.

    4. **Generación de trayectorias**:
       - Añade un botón para invocar el operador `object.create_trayectoria`, que genera la trayectoria interpolada basada en los parámetros configurados.

    Atributos:
    ----------
    - `bl_label` : str
        Nombre visible del panel.
    - `bl_idname` : str
        Identificador único del panel.
    - `bl_space_type` : str
        Espacio de trabajo donde aparece el panel.
    - `bl_region_type` : str
        Región de la interfaz donde se dibuja el panel.
    - `bl_category` : str
        Categoría del panel en la barra lateral.

    Métodos:
    --------
    draw(context):
        Dibuja los elementos del panel en la interfaz.
        - Muestra controles dinámicos según las propiedades configuradas en la escena y el objeto activo.
        - Incluye un botón para ejecutar el operador de creación de trayectorias.
        '''

    bl_label = "Drivers Control"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Drivers Control"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Generación trayectoria interpolada")
        layout.prop(context.scene, "selected_shape", text="Elige una forma")

        if context.scene.selected_shape == 'CATMULL-ROM':
            layout.prop(context.scene, "tension", text="Tensión Catmull-Rom")

        obj = context.object

        if context.scene.selected_shape == 'HERMITE':
            obj = context.object
            if obj and hasattr(obj, "velocity"):
                layout.prop(obj, "velocity", text="Velocidad Hermite")

        # Verificamos si `obj` se ha definido antes de usarlo
        if obj:
            layout.prop(obj, "eje_alineacion")
            layout.prop(obj, "eje_arriba")
            layout.prop(obj, "angulo_rotacion")
            layout.prop(obj, "control_vel")

            if obj.control_vel:
                layout.prop(obj, "distancia_deseada")

        layout.operator("object.create_trayectoria", text="Crear trayectoria")


class OBJECT_OT_CreateTrayectoria(bpy.types.Operator):
    '''
    Operador para crear trayectorias interpoladas y configurar drivers en Blender.

    Propósito:
    ----------
    Este operador permite generar trayectorias animadas utilizando diferentes métodos de interpolación
    y asignar drivers a las propiedades de posición y rotación del objeto seleccionado. Además, ajusta
    los keyframes y asegura que las trayectorias sean visibles en la vista 3D.

    Atributos:
    ----------
    - `bl_idname` : str
        Identificador único del operador. Se usa para invocarlo en scripts y desde la interfaz.
        En este caso: "object.create_trayectoria".
    - `bl_label` : str
        Nombre visible del operador en la interfaz.
        En este caso: "Crear Trayectoria".

    Propiedades:
    ------------
    - `shape` : EnumProperty
        Tipo de interpolación que se utilizará para generar la trayectoria.
        - **name:** "Tipo de interpolación".
        - **description:** "Selecciona la interpolación".
        - **items:** Una lista de tipos de interpolación (definidos en `enum_items`).
        - **default:** 'LINEAL'.

    Métodos:
    --------
    1. `invoke(self, context, event)`:
        Método invocado cuando se utiliza el operador desde la interfaz (por ejemplo, al hacer clic en un botón).
        Configura los drivers y los ajustes necesarios antes de crear la trayectoria.

        Retorna:
        --------
        - {'FINISHED'}: Indica que el operador se ejecutó correctamente.

    2. `execute(self, context)`:
        Método que se ejecuta directamente desde un script o cuando el operador se activa sin interacción del usuario.
        Realiza las mismas operaciones que `invoke`.

        Retorna:
        --------
        - {'FINISHED'}: Indica que el operador se ejecutó correctamente.
        '''

    bl_idname = "object.create_trayectoria"
    bl_label = "Crear Trayectoria"

    shape = bpy.props.EnumProperty(
        name="Tipo de interpolación",
        description="Selecciona la interpolación",
        items=enum_items,
        default='LINEAL'
    )

    def invoke(self, context, event):
        obj = context.object

        if not obj.control_vel:
            longitud_recorrida(obj)

        asigna_driver_posicion(context.object)
        #sincronizar_keyframes_velocidad(context.object)

        if obj.rotation_mode != 'QUATERNION':
            obj.rotation_mode = 'QUATERNION'

        asigna_drivers_rotacion(context.object)

        bpy.ops.object.paths_calculate(display_type='RANGE', range='SCENE')
        bpy.ops.object.paths_update_visible()

        self.report({'INFO'}, "Trayectoria creada exitosamente")
        return {'FINISHED'}

    def execute(self, context):
        obj = context.object
        asigna_driver_posicion(context.object)
        #sincronizar_keyframes_velocidad(context.object)

        if obj.rotation_mode != 'QUATERNION':
            obj.rotation_mode = 'QUATERNION'

        asigna_drivers_rotacion(context.object)

        bpy.ops.object.paths_calculate(display_type='RANGE', range='SCENE')
        bpy.ops.object.paths_update_visible()

        self.report({'INFO'}, "Trayectoria creada exitosamente")
        return {'FINISHED'}


class OBJECT_PT_VelocityPanel(bpy.types.Panel):
    '''
    Panel personalizado para controlar la velocidad de un objeto en Blender.

    Propósito:
    ----------
    Este panel se utiliza para mostrar y permitir la edición de la propiedad
    "velocity" de un objeto seleccionado en la ventana de Propiedades.

    Atributos:
    ----------
    - `bl_label` : str
        Título visible del panel en la interfaz.
        En este caso: "Control de Velocidad".
    - `bl_idname` : str
        Identificador único del panel. Se utiliza para invocarlo o referenciarlo en código.
        En este caso: "OBJECT_PT_velocity_panel".
    - `bl_space_type` : str
        Define el espacio donde se muestra el panel.
        En este caso: 'PROPERTIES' (panel de propiedades).
    - `bl_region_type` : str
        Define la región dentro del espacio en la que aparece el panel.
        En este caso: 'WINDOW'.
    - `bl_context` : str
        Contexto en el que se muestra el panel.
        En este caso: 'object' (panel relacionado con objetos).

    Métodos:
    --------
    1. `draw(self, context)`:
        Método que define el contenido del panel.
        - Muestra una propiedad llamada "velocity" para el objeto actualmente seleccionado.

        Parámetros:
        -----------
        - `context`: Contexto actual de Blender, que proporciona acceso al objeto seleccionado.
    '''

    bl_label = "Control de Velocidad"
    bl_idname = "OBJECT_PT_velocity_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj:
            layout.prop(obj, "velocity")


def register():
    '''
    Registra las clases, propiedades y funciones necesarias en el contexto de Blender.

    Propósito:
    ----------
    Configurar y registrar los elementos personalizados del script en el entorno de Blender.
    Esto incluye paneles, operadores, propiedades de escena y funciones utilizadas como drivers.
    '''

    bpy.app.driver_namespace['get_pos2'] = get_posicion2
    bpy.app.driver_namespace['get_pos1'] = get_posicion1
    bpy.app.driver_namespace['get_posicion_x_loop'] = get_posicion_x_loop
    bpy.app.driver_namespace['get_posicion_y_loop'] = get_posicion_y_loop
    bpy.app.driver_namespace["get_quaternion"] = get_quaternion

    bpy.utils.register_class(OBJECT_PT_CustomPanel)
    bpy.utils.register_class(OBJECT_OT_CreateTrayectoria)
    bpy.utils.register_class(OBJECT_PT_VelocityPanel)

    print("Definimos Drivers")


def unregister():
    '''
    Desregistra las clases, propiedades y funciones previamente registradas en Blender.

    Propósito:
    ----------
    Limpia el entorno de Blender eliminando los elementos personalizados registrados por el script.

    '''
    bpy.utils.unregister_class(OBJECT_PT_CustomPanel)
    bpy.utils.unregister_class(OBJECT_OT_CreateTrayectoria)
    bpy.utils.unregister_class(OBJECT_PT_VelocityPanel)


if __name__ == "__main__":
    '''
    Bloque principal que se ejecuta si el script se ejecuta directamente.

    Propósito:
    ----------
    Registrar los elementos necesarios y asignar drivers al objeto activo si está disponible.
    '''

    register()

    obj_activo = bpy.context.view_layer.objects.active

    if obj_activo:
        asigna_driver_posicion(obj_activo)
        print("drivers asignados")
    else:
        print("No hay obj activo / driver no asignado")
