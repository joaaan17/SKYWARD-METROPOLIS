# Repositorio para la asignatura Animación del Grado en Ingeniería Multimedia.
## Grupo 05
### Miembros:
- Joan Girón
- David González
- Javier García
- 
## Práctica 1: Control Procedural del Movimiento en Blender

### Introducción

Esta herramienta ha sido desarrollada con el objetivo de automatizar la generación de trayectorias para objetos dentro de Blender, utilizando algoritmos de interpolación y drivers personalizados. De esta manera, se facilita el control procedimental del movimiento, permitiendo la creación de animaciones complejas sin tener que definir manualmente cada fotograma clave. La herramienta se integra como un complemento de Blender, haciendo uso de su API en Python, y está diseñada para ser intuitiva y flexible para usuarios con un conocimiento básico de Blender y Python.

### Funcionalidades

1. **Generación de Trayectorias con Drivers**
La herramienta utiliza drivers de Blender para controlar la posición de un objeto. Los drivers permiten calcular las coordenadas de un objeto en cualquier fotograma, utilizando funciones predefinidas. Se han implementado varios tipos de interpolación para generar trayectorias suaves y adaptables según los requerimientos de la animación.

Los principales tipos de interpolación soportados son:
- Interpolación Lineal: Para un movimiento constante y uniforme entre puntos de control.
- Catmull-Rom: Genera una curva suave pasando por todos los puntos de control, ideal para trayectorias que requieran un comportamiento natural.
- Hermite: Proporciona mayor control sobre la velocidad y la forma de la curva, permitiendo definir tangentes en los puntos de control para ajustar el movimiento de forma precisa.

2. **Integración en la Interfaz de Blender**
Se ha creado un panel en la interfaz de Blender para facilitar el uso de la herramienta:
Selector de Método de Interpolación: El usuario puede elegir entre los métodos mencionados (Lineal, Catmull-Rom, Hermite).
Control de Tensión: En el caso de Catmull-Rom, se incluye un deslizador para ajustar la tensión de la curva, lo que permite modificar el grado de suavidad del movimiento.

3. **Automatización de Drivers**
La herramienta automatiza la creación de drivers para las coordenadas del objeto, evitando la necesidad de configurarlos manualmente en Blender. Esto se realiza mediante una función que asigna los drivers a las coordenadas, asegurando que se sigan las trayectorias definidas por los fotogramas clave y simplificando el flujo de trabajo.

### Instrucciones de Uso

1. **Instalación del Complemento**
Descargar el archivo ZIP del complemento desde el repositorio del grupo de trabajo.
En Blender, ir a Edit > Preferences > Add-ons.
Seleccionar Install..., elegir el archivo ZIP y habilitar el complemento.

2. **Uso del Panel de Interpolación**
Seleccione un objeto en la escena.
En la sección View 3D > UI > Mi Addon, encontrará el panel de control.
Seleccione el Método de Interpolación adecuado para la trayectoria que desea crear.
Si ha seleccionado Catmull-Rom, ajuste la tensión según las necesidades de la animación.
Pulse el botón para Asignar Drivers y el objeto debería comenzar a seguir la trayectoria definida por los fotogramas clave.

3. **Inserción de Fotogramas Clave**
Los fotogramas clave se insertan manualmente en la posición del objeto utilizando la interfaz de Blender. La herramienta luego interpolará entre estos puntos usando el método seleccionado.
Al insertar fotogramas clave, se recomienda definir trayectorias que permitan verificar el comportamiento de cada tipo de interpolación, para así evaluar su efectividad.

---

## Práctica 2: Coches voladores en la Ciudad Procedural

### Introducción

En esta práctica, comparado a la anterior, se amplió la funcionalidad del complemento de Blender para integrar vehículos voladores que se desplazan por una ciudad generada proceduralmente. Los coches siguen trayectorias específicas a través de las calles, incluyendo movimientos oscilatorios y giros en intersecciones.

### Funcionalidades

1. **Creación de Coches Voladores**
   - El complemento permite generar coches (en forma de esferas), ubicándolos al inicio de una calle seleccionada aleatoriamente. Los coches tienen propiedades configurables, como velocidad y su posición inicial, las cuales el usuario ajusta desde el panel de control.

2. **Interpolación del Movimiento**
   - Las trayectorias de los coches son generadas utilizando el módulo de interpolación desarrollado en la Práctica 1. Esto a su vez depende del usuario el cual desde el panel de control seleccionara la interpolación que este quiere que se apliquen en las esferas para generar un movimiento fluido y controlado a lo largo de las calles.

3. **Oscilación Aleatoria**
   - Se implementó un desplazamiento aleatorio opcional en los ejes de las esferas, utilizando funciones de ruido. Esto rompe la monotonía del movimiento lineal y simula un comportamiento más realista.
   - Parámetros ajustables desde el panel: amplitud, frecuencia y ejes en los que se aplica la oscilación.

4. **Creación de Múltiples Coches**
   - El complemento permite configurar la cantidad de coches a generar en la escena. Cada coche se crea con características independientes y puede seguir trayectorias únicas.

5. **Giros en las Intersecciones**
   - Los coches pueden realizar giros de 90 grados en las intersecciones, siguiendo rutas predefinidas o generadas aleatoriamente. Esto se logra insertando automáticamente fotogramas clave en las coordenadas necesarias.

6. **Automatización del Borrado**
   - Para facilitar las pruebas, se añadió un botón que elimina rápidamente todos los coches (esferas) de la escena.

### Instrucciones de Uso

1. **Configuración del Panel de Coches Voladores**
   - Configura la velocidad, cantidad de coches y parámetros de oscilación desde el panel del complemento.
   - Presiona el botón para generar coches en la ciudad.

2. **Creación y Visualización**
   - Los coches seguirán automáticamente las trayectorias definidas, girando en intersecciones y mostrando movimientos oscilatorios en el eje vertical.

---

## Práctica 3: Orientación a lo Largo de una Trayectoria

### Introducción

En esta práctica, se implementó una funcionalidad adicional que permite a los vehículos rotar y alinearse con la dirección de su trayectoria. Además, se añadió la capacidad de controlar la inclinación lateral de los vehículos y la posibilidad de cargar modelos 3D externos.

### Funcionalidades

1. **Orientación de Vehículos**
   - Se calculan los cuaterniones necesarios para alinear el eje frontal del vehículo con la dirección de su movimiento.
   - Los drivers generados controlan dinámicamente las rotaciones en cada fotograma.

2. **Carga de Modelos 3D Externos**
   - Los usuarios pueden cargar un modelo 3D en formato `.obj` desde un explorador gráfico, reemplazando los vehículos predeterminados (esferas), por el modelo de coches proporcionado en la práctica.

3. **Control de la Inclinación Lateral**
   - Los vehículos pueden inclinarse lateralmente al girar, simulando el comportamiento natural en curvas.
   - El ángulo de inclinación es ajustable desde el panel.

4. **Integración con el Sistema de Interpolación**
   - La interpolación de la posición y la orientación se realiza de forma sincronizada.

### Instrucciones de Uso

1. **Configuración de la Orientación**
   - Define el eje del vehículo que se alineará con la dirección del movimiento desde el panel.
   - Activa el control de rotación y ajusta parámetros como la inclinación lateral.

2. **Carga de Modelos Externos**
   - Usa el explorador de archivos para seleccionar el archivo `car.obj` como modelo del vehículo.

---

## Práctica 4: Control de la Velocidad en una Curva

### Introducción

En esta práctica se busca ampliar el sistema de interpolación desarrollado previamente para controlar de manera precisa la velocidad a lo largo de una trayectoria. Hasta ahora, las trayectorias se definían mediante posiciones en fotogramas clave, pero no se podía garantizar una velocidad constante ni controlada, a partir de ahora sí se podrá.

### Funcionalidades

1. **Parametrización por la Longitud de Arco**
   - Se calcula la longitud de arco acumulada de la trayectoria mediante muestreo de puntos en intervalos regulares.
   - Los resultados se almacenan en una propiedad del objeto llamada "distancia_recorrida".

2. **Reparametrización para Velocidad Constante**
   - El sistema ajusta el parámetro de entrada (fotograma o tiempo) para garantizar que el objeto recorra 1 metro por segundo a lo largo de la trayectoria.
   - La implementación utiliza la función frame_desde_longitud() para mapear la distancia deseada al fotograma correspondiente, asegurando un movimiento uniforme.

3. **Control Personalizado de Velocidad**
   - Una nueva propiedad llamada "distancia_deseada" permite definir la distancia que el objeto debe recorrer en cada fotograma, permitiendo modificar dinámicamente la velocidad.
   - Este método permite generar aceleraciones y desaceleraciones ajustando los valores de distancia_deseada a través de fotogramas clave.

4. **Integración en la Interfaz**
   - El panel del complemento ahora incluye una opción para activar o desactivar el control de velocidad.
   - Es posible modificar la velocidad en diferentes tramos de la trayectoria ajustando manualmente los valores de distancia_deseada.

5. **Sincronización con la Orientación**
   - Se asegura que el cambio de parametrización afecte tanto a la posición como a la orientación del objeto, garantizando que las rotaciones sean consistentes con el nuevo control de velocidad.

### Instrucciones de Uso

1. **Configuración Inicial**
   - Activa el control de velocidad desde el panel del complemento.
   - Pulsa el botón para generar la trayectoria, lo que inicializa los fotogramas clave necesarios para la propiedad distancia_deseada.

2. **Personalización de Velocidad**
   - Inserta nuevos fotogramas clave sobre distancia_deseada para personalizar la velocidad en diferentes partes de la trayectoria.

---

### Enlaces a los Vídeos

- **Práctica 1**: [https://www.youtube.com/watch?v=ezUhcsXmMwk&ab_channel=ANI_DJJ]
- **Práctica 2**: [https://youtu.be/2KJUw3roKng]
- **Práctica 3**: [https://youtu.be/XK521YXMky8]
- **Práctica 4**: [https://youtu.be/rngKevSq1Es]
- **Rigging & Motion Capture**:
   - **Explicaciones**: [https://youtu.be/FdycfFrMt3Y]
   - **Renders**: [https://youtu.be/_1TZZupYLxw]

---