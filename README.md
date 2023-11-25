
## Configuración del Entorno

- Asegúrate de tener instalado Python 3.x.
- Crea un entorno virtual: `python -m venv venv`.
- Activa el entorno virtual:
    - En Windows: `venv\Scripts\activate`
    - En Unix o MacOS: `source venv/bin/activate`
- Instala las dependencias: `pip install -r requirements.txt`.

## Preparación del Entorno
- Ejecuta 
```bash
flask db init
flask db migrate
flask db upgrade
```

## Ejecución del Proyecto

- Ejecuta la aplicación: `flask run`.
- Abre un navegador y visita `http://localhost:5000`.

## Contribuciones

Si deseas contribuir al proyecto, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una rama para tu contribución: `git checkout -b feature/nueva-funcionalidad`.
3. Realiza tus cambios y haz commit: `git commit -m "Añade nueva funcionalidad"`.
4. Haz push a tu rama: `git push origin feature/nueva-funcionalidad`.
5. Abre un Pull Request en GitHub.

## Problemas y Sugerencias

Si encuentras algún problema o tienes sugerencias, por favor crea un nuevo [issue](.github/ISSUE_TEMPLATE).

## Licencia

Este proyecto está licenciado bajo [Nombre de la Licencia]. Consulta el archivo LICENSE para más detalles.
