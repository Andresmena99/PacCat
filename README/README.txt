
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
    - Filtro:
	1) En la pagina de join game, no hemos implementado un filtro, ya que lógicamente en este listado solo se muestran películas cuyo estado es creado, en las que te puedes unir como raton, por lo que filtrar de cualquier forma haría que no se mostrase ninguna película
	2) El filtro por estado de la partida propuesto nos parecía inutil, ya que en join game siempre son created, en select game siempre active, y en reproduce game siempre finished. Por ello, hemos implementado filtros distintos, como por ejemplo mostrar partidas que he ganado yo (en el modo cine), o mostrar las partidas en las que es mi turno (a la hora de seleccionar). En funcion de la página, el id del filtro tiene un mensaje especifico u otro.
