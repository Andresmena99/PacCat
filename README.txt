
Entrega de juego Raton Gato.

Autores:
    Eric Morales
    Andrés Mena

Se entrega todo lo necesario para la ejecución de la aplicación de ratón gato:
    - Carpeta ratonGato con las aplicaciones logic y datamodel completas.
    - Archivo coverage.txt en el que se detalla la ejecucion del comando.
    - Capturas de pantalla con las ejecuciones los tests y su coverage:
        + Se incluyen cuatro capturas, dos en local y dos en heroku, son dos
        para poder apreciar la mejora de coverage que conseguimos añadiendo
        nuestros tests_extra.py, que suben el coverage de 92% a 96%.
    - Nuestros tests propios.

Aclaraciones:
    - Se ha añadido la funcionalidad de comprobar ganador, la cual debería
      entregarse en la siguiente práctica. En caso de que haya un ganador, hemos
      decidido que se muestre una página en la que ponga si el ganador ha sido
      el gato o el ratón, y que muestre la última situación del tablero, para
      que los jugadores puedan ver cómo han perdido. Ademas, la partida pasa a
      estado finalizado y se saca de la sesión. La hemos incorporado en el
      apartado del modelo de datos, y cuando se guarda la partida comprobamos
      si hay un ganador. El algoritmo para determinarlo todavía no esta
      depurado, realizamos las siguientes comprobaciones:
        + Si el ratón no tiene ninguna casilla del tablero donde moverse,
          significa que ha perdido, porque ha sido rodeado
        + Si el ratón se encuentra en la misma fila que el ultimo gato, significa
          que ha ganado, ya que, siempre que realice movimientos lógicos, sin
          volver hacia atrás, no puede ser encerrado por los gatos

    - Todo el código se encuentra documentado siguiendo los criterios usados
    en numpy.
    Fuente: https://numpydoc.readthedocs.io/en/latest/format.html#class-docstring

    - La aplicación se encuentra desplegada en heroku en el siguiente enlace:
    Link: https://infinite-tor-36623.herokuapp.com/

Test adicional no trivial:
    - Aprovechando la funcionalidad añadida de finalización de partidas, hemos
    creado una nueva clase de tests, llamada CheckGameWinner, que se encuentra
    en la carpeta raiz del proyecto

    En esta clase, tenemos dos tests, en los que comprobamos que el juego
    finaliza correctamente. Estos test se encuentran documentados en el fichero,
    pero a modo de resumen realizan lo siguiente:

    - Test1: Secuencia de movimientos que hacen que el raton pierda,
      porque queda encerrado. Creamos la partida, la metemos en la sesion, y
      ejecutamos los movimientos. En cada movimiento comprobamos que no se haya
      dado una condicion de victoria (excepto en el último movimiento,
      logicamente) y comprobamos que la partida siga activa. Cuando el raton
      queda encerrado, comprobamos que se nos encontramos en una pagina con el
      mensaje de error, que la partida ha pasado a estado finalizado, y que ya
      no se encuentra en la sesión

    - Test2: Realizamos lo mismo que en el test anterior, pero en este caso
      la secuencia de movimientos nos lleva a la victoria del raton
