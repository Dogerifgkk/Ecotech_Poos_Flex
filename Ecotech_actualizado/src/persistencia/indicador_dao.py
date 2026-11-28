# persistencia/indicador_dao.py
from persistencia.conexion import marcador, obtener_motor, transaccion
from dominio.indicador import Indicador


class IndicadorDAO:
    @staticmethod
    def guardar(indicador: Indicador):
        """Una fila por (código, fecha). Si ya existe, actualiza el valor."""
        m = marcador()
        if obtener_motor() == "sqlite":
            sql = (f"INSERT INTO indicador (codigo, fecha, valor) VALUES ({m}, {m}, {m}) "
                   "ON CONFLICT(codigo, fecha) DO UPDATE SET valor = excluded.valor")
        else:
            sql = (f"INSERT INTO indicador (codigo, fecha, valor) VALUES ({m}, {m}, {m}) "
                   "ON DUPLICATE KEY UPDATE valor = VALUES(valor)")
        with transaccion() as cursor:
            cursor.execute(sql, (indicador.codigo, indicador.fecha, indicador.valor))
        return indicador

    @staticmethod
    def ultimo(codigo):
        """Observación más reciente (por fecha publicada) o None si no hay."""
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(
                "SELECT codigo, fecha, valor FROM indicador "
                f"WHERE codigo = {m} ORDER BY fecha DESC LIMIT 1",
                (codigo,),
            )
            fila = cursor.fetchone()
        return None if fila is None else Indicador(fila[0], fila[1], fila[2])

    @staticmethod
    def contar(codigo, fecha):
        m = marcador()
        with transaccion() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM indicador WHERE codigo = {m} AND fecha = {m}",
                (codigo, fecha),
            )
            return cursor.fetchone()[0]
