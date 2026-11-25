# dominio/indicador.py
from datetime import datetime


class Indicador:
    """Una observación publicada: código (uf, dolar), fecha del dato y valor."""
    MAX_CODIGO = 10

    def __init__(self, codigo, fecha, valor):
        self.codigo = self.validar_codigo(codigo)
        self.fecha = self.validar_fecha(fecha)
        self.valor = self.validar_valor(valor)

    @classmethod
    def validar_codigo(cls, codigo):
        if not isinstance(codigo, str):
            raise ValueError("El código del indicador debe ser texto.")
        codigo = codigo.strip().lower()
        if not 0 < len(codigo) <= cls.MAX_CODIGO or not codigo.isalnum():
            raise ValueError("Código de indicador no válido.")
        return codigo

    @staticmethod
    def validar_fecha(fecha):
        """Acepta 'AAAA-MM-DD' o un texto ISO ('2026-01-05T03:00:00.000Z').
        Se conserva la fecha publicada, no la del reloj de hoy."""
        if not isinstance(fecha, str) or len(fecha) < 10:
            raise ValueError("Fecha de indicador no válida.")
        texto = fecha[:10]
        try:
            datetime.strptime(texto, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Fecha de indicador no válida.") from None
        return texto

    @staticmethod
    def validar_valor(valor):
        if isinstance(valor, bool):
            raise ValueError("Valor de indicador no válido.")
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            raise ValueError("Valor de indicador no válido.") from None
        if valor != valor or valor in (float("inf"), float("-inf")) or valor <= 0:
            raise ValueError("El valor del indicador debe ser un número positivo.")
        return valor

    def __repr__(self):
        return f"Indicador(codigo={self.codigo!r}, fecha={self.fecha!r}, valor={self.valor})"
