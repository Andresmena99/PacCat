
Entrega de juego PacCat.

Autores:
    Eric Morales
    Andrés Mena

Se entrega todo lo necesario para la ejecución de la aplicación de PacCat:
    - Archivo coverage.txt en el que se detalla la ejecucion del comando.
    - Capturas de pantalla con las ejecuciones los tests y su coverage.
    - Nuestros tests propios.

Aclaraciones:
    - Filtro:
        En función de la pagina en la que estamos, el filtro tiene una opciones
        u otras

        Hemos implementado el filtro en la seccion unirse a partida, que,
        aunque de momento en la funcionalidad de la aplicación siempre nos
        vamos a unir como PAC (porque al crearse una partida, siempre se asigna
        automáticamente el gato al nuevo jugador), para futura funcionalidad
        de la aplicacion en la que se pueda decidir como qué personaje quieres
        iniciar la partida
    - Condicion de victoria:
        El PAC gana cuando consigue llegar arriba del todo. Los gatos
        (fantasmas) ganan cuando rodean al PAC.

    - Counter: hemos decidido dejarlo visible y cuenta todos los errores que ocurren,
    tanto errores de sesión como errores, globales (urls no validos, por ejemplo).

    - Usuario alumnodb. Tiene una serie de partidas jugadas, para que puedas
        reproducirlas directamente. Es superusuario
        Usuario: alumnodb
        Contraseña: alumnodb
    - Usuario jorgedelaspennas. No es superusuario, pero tiene partidas jugadas,
    y algunas pendientes con alumnodb.
        Usuario: jorgedelaspennas
        Contraseña: alumnodb