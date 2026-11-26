"""Consulta SQLite desde la terminal de Visual Studio Code."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path


def main():
    archivo = Path(__file__).resolve().with_name('elearning.db')
    parser = argparse.ArgumentParser(description='Muestra la ubicación y los datos de SQLite.')
    parser.add_argument('tabla', nargs='?', help='Tabla que quieres consultar, por ejemplo usuarios o cursos.')
    parser.add_argument('--pagina', type=int, default=1, help='Página de 50 registros, comenzando en 1.')
    args = parser.parse_args()
    if args.pagina < 1:
        parser.error('La página debe ser mayor que cero.')
    print(f'Archivo de base de datos\n{archivo}\n')
    if not archivo.is_file():
        parser.error('La base todavía no existe. Inicia la aplicación o ejecuta seed.py.')
    with closing(sqlite3.connect(archivo.as_uri() + '?mode=ro', uri=True)) as conexion:
        tablas = [fila[0] for fila in conexion.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        print('TABLAS Y CANTIDAD DE REGISTROS')
        for tabla in tablas:
            nombre = tabla.replace('"', '""')
            total = conexion.execute(f'SELECT COUNT(*) FROM "{nombre}"').fetchone()[0]
            print(f'  {tabla:<18} {total}')
        if args.tabla is None:
            print('\nPara ver usuarios, ejecuta: python ver_base_datos.py usuarios')
            return
        if args.tabla not in tablas:
            parser.error('La tabla indicada no existe.')
        nombre = args.tabla.replace('"', '""')
        columnas = [fila[1] for fila in conexion.execute(f'PRAGMA table_info("{nombre}")') if fila[1] != 'password_hash']
        seleccion = ', '.join('"' + columna.replace('"', '""') + '"' for columna in columnas)
        filas = conexion.execute(f'SELECT {seleccion} FROM "{nombre}" ORDER BY id LIMIT 50 OFFSET ?', ((args.pagina - 1) * 50,)).fetchall()
        print(f'\nTABLA {args.tabla} - PÁGINA {args.pagina}')
        if args.tabla == 'usuarios':
            print('Las contraseñas se almacenan como hash en la base de datos.')
        for fila in filas:
            print('\n' + ' | '.join(f'{columna}: {valor}' for columna, valor in zip(columnas, fila)))
        if not filas:
            print('Esta página no contiene registros.')


if __name__ == '__main__':
    main()
