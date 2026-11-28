# test_ecotech.py: pruebas automáticas con una BD temporal (SQLite) y una API simulada.
# Ejecutar desde la carpeta src:   py -m unittest test_ecotech -v
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

import bcrypt
import requests

os.environ["DB_ENGINE"] = "sqlite"          # las pruebas siempre usan SQLite temporal

from dominio.indicador import Indicador                      # noqa: E402
from dominio.reporte import ReporteEmpleados, ReportePorDepartamento  # noqa: E402
from dominio.usuario import Usuario                          # noqa: E402
from empleado import Empleado                                # noqa: E402
from departamento import Departamento                        # noqa: E402
from persistencia.conexion import ErrorBD, ErrorIntegridad, abrir_conexion  # noqa: E402
from persistencia.crear_bd import crear_tablas               # noqa: E402
from persistencia.departamento_dao import DepartamentoDAO    # noqa: E402
from persistencia.empleado_dao import EmpleadoDAO            # noqa: E402
from persistencia.indicador_dao import IndicadorDAO          # noqa: E402
from persistencia.semilla import sembrar                     # noqa: E402
from persistencia.usuario_dao import UsuarioDAO              # noqa: E402
from presentacion import menu_empleados, menu_usuario        # noqa: E402
from servicios import api_indicadores, empleados as srv      # noqa: E402
from servicios.autenticacion import autenticar, registrar_usuario  # noqa: E402
from servicios.indicadores import actualizar_uf, consultar_guardado  # noqa: E402
from servicios.permisos import exigir_admin, exigir_sesion   # noqa: E402

_GENSALT_REAL = bcrypt.gensalt      # la función original, antes de simularla
JSON_UF = {"codigo": "uf", "serie": [{"fecha": "2026-01-05T03:00:00.000Z", "valor": 40000.0}]}


def _respuesta(json_datos):
    r = mock.Mock()
    r.raise_for_status.return_value = None
    r.json.return_value = json_datos
    return r


class Base(unittest.TestCase):
    def setUp(self):
        # bcrypt con pocas rondas SOLO en las pruebas (así corren rápido)
        rapido = mock.patch("servicios.autenticacion.bcrypt.gensalt",
                            lambda: _GENSALT_REAL(rounds=4))
        rapido.start()
        self.addCleanup(rapido.stop)
        self._dir = tempfile.TemporaryDirectory()
        os.environ["DB_NAME"] = os.path.join(self._dir.name, "prueba.db")
        crear_tablas()
        sembrar()
        self.admin = autenticar("admin", "Admin2026!")
        self.ana = autenticar("ana_lopez", "Ana2026!")

    def tearDown(self):
        self._dir.cleanup()

    def contar(self, tabla):
        con = abrir_conexion()
        n = con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
        con.close()
        return n


class TestDominio(Base):
    def test_validaciones_empleado(self):
        self.assertEqual(Empleado.validar_nombre("  ana   lopez "), "Ana Lopez")
        self.assertEqual(Empleado.validar_correo(" ANA@Ecotech.cl "), "ana@ecotech.cl")
        for malo in ("ana@", "ana", "@mail.cl", "a b@mail.cl"):
            with self.assertRaises(ValueError):
                Empleado.validar_correo(malo)
        with self.assertRaises(ValueError):
            Empleado("a", "ana@mail.cl")

    def test_paso5_setter_departamento(self):
        e = Empleado("ana lopez", "ana@mail.cl")
        e.departamento = Departamento("Ventas")
        e.departamento = None
        with self.assertRaises(ValueError):
            e.departamento = "Ventas"

    def test_agregar_empleado_no_duplica(self):
        d, e = Departamento("Ventas"), Empleado("ana lopez", "ana@mail.cl")
        d.agregar_empleado(e)
        d.agregar_empleado(e)
        self.assertEqual(len(d.empleados), 1)
        self.assertIs(e.departamento, d)

    def test_reportes_polimorfismo(self):
        d = DepartamentoDAO.buscar_con_empleados(1)
        todos = EmpleadoDAO.listar()
        general = ReporteEmpleados(todos).generar()
        por_dep = ReportePorDepartamento(d).generar()
        self.assertIn("Reporte general", general)
        self.assertIn("Departamento: Soporte", por_dep)
        self.assertIn(f"Total: {len(todos)}", general)
        self.assertIn("Total: 2", por_dep)

    def test_usuario_validaciones(self):
        self.assertEqual(Usuario.normalizar_usuario(" Ana.Torres "), "ana.torres")
        with self.assertRaises(ValueError):
            Usuario.normalizar_usuario("ñandú")
        with self.assertRaises(ValueError):
            Usuario("abc", "h", 0)
        with self.assertRaises(ValueError):
            Usuario("abc", "h", 1, rol="superadmin")
        self.assertEqual(Usuario.validar_clave(" Ab 12 "), " Ab 12 ")
        with self.assertRaises(ValueError):
            Usuario.validar_clave("12345")

    def test_indicador_validaciones(self):
        i = Indicador("UF", "2026-01-05T03:00:00.000Z", "40000")
        self.assertEqual((i.codigo, i.fecha, i.valor), ("uf", "2026-01-05", 40000.0))
        for args in (("uf", "no-fecha", 1), ("uf", "2026-01-05", -3), ("uf", "2026-01-05", "x")):
            with self.assertRaises(ValueError):
                Indicador(*args)


class TestPersistencia(Base):
    def test_semilla_repetible(self):
        antes = {t: self.contar(t) for t in ("empleado", "departamento", "usuario")}
        sembrar()
        sembrar()
        despues = {t: self.contar(t) for t in ("empleado", "departamento", "usuario")}
        self.assertEqual(antes, despues)

    def test_relacion_persistida_y_reconstruida(self):
        d = DepartamentoDAO.buscar_con_empleados(1)
        self.assertEqual(sorted(e.nombre for e in d.empleados), ["Ana Lopez", "Luis Perez"])
        vacio = DepartamentoDAO.buscar_con_empleados(4)
        self.assertEqual(vacio.empleados, [])
        self.assertIsNone(DepartamentoDAO.buscar_con_empleados(999))

    def test_asignar_y_reasignar(self):
        pedro = EmpleadoDAO.buscar_por_correo("pedro@ecotech.cl")
        self.assertIsNone(pedro.departamento)
        ventas = [d for d in DepartamentoDAO.listar() if d.nombre == "Ventas"][0]
        self.assertEqual(srv.asignar_departamento(self.admin, pedro, ventas), 1)
        self.assertEqual(srv.asignar_departamento(self.admin, pedro, ventas), 1)  # repetir
        self.assertEqual(EmpleadoDAO.buscar_por_id(pedro.id).departamento.nombre, "Ventas")
        self.assertEqual(len(DepartamentoDAO.buscar_con_empleados(ventas.id).empleados), 2)

    def test_crud_empleado(self):
        e = srv.registrar_empleado(self.admin, "nuevo empleado", "nuevo@ecotech.cl")
        self.assertIsNotNone(e.id)
        with self.assertRaises(ValueError):                    # correo repetido
            srv.registrar_empleado(self.admin, "otro", "nuevo@ecotech.cl")
        self.assertEqual(srv.actualizar_correo(self.admin, e, "cambio@ecotech.cl"), 1)
        self.assertEqual(EmpleadoDAO.buscar_por_id(e.id).correo, "cambio@ecotech.cl")
        self.assertEqual(srv.eliminar_empleado(self.admin, e.id), 1)
        self.assertIsNone(EmpleadoDAO.buscar_por_id(e.id))
        self.assertEqual(srv.eliminar_empleado(self.admin, e.id), 0)   # ya no existe

    def test_eliminar_con_cuenta_es_rechazado_por_la_bd(self):
        ana = EmpleadoDAO.buscar_por_correo("ana@ecotech.cl")
        with self.assertRaises(ErrorIntegridad):
            srv.eliminar_empleado(self.admin, ana.id)
        self.assertIsNotNone(EmpleadoDAO.buscar_por_id(ana.id))

    def test_migracion_agrega_rol(self):
        os.environ["DB_NAME"] = os.path.join(self._dir.name, "antigua.db")
        con = sqlite3.connect(os.environ["DB_NAME"])
        con.execute("CREATE TABLE usuario (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "empleado_id INTEGER NOT NULL UNIQUE, nombre_usuario TEXT NOT NULL UNIQUE, "
                    "password_hash TEXT NOT NULL)")
        con.commit()
        con.close()
        crear_tablas()
        con = sqlite3.connect(os.environ["DB_NAME"])
        columnas = [f[1] for f in con.execute("PRAGMA table_info(usuario)")]
        con.close()
        self.assertIn("rol", columnas)


class TestAutenticacion(Base):
    def test_hash_no_es_la_clave_y_login_correcto(self):
        cuenta = UsuarioDAO.buscar_por_nombre("ana_lopez")
        self.assertNotIn("Ana2026!", cuenta.password_hash)
        self.assertTrue(cuenta.password_hash.startswith("$2"))
        self.assertEqual(self.ana.rol, "empleado")
        self.assertEqual(self.admin.rol, "admin")

    def test_rol_persiste_al_reiniciar(self):
        otra_vez = autenticar("  ADMIN ", "Admin2026!")     # normaliza el usuario
        self.assertEqual((otra_vez.nombre_usuario, otra_vez.rol), ("admin", "admin"))

    def test_rechazos(self):
        self.assertIsNone(autenticar("ana_lopez", "clave-incorrecta"))
        self.assertIsNone(autenticar("no_existe", "Ana2026!"))
        self.assertIsNone(autenticar("ana_lopez", ""))
        self.assertIsNone(autenticar("ana_lopez", "x" * 80))
        self.assertIsNone(autenticar("ana_lopez", None))

    def test_registro_sin_duplicados(self):
        pedro = EmpleadoDAO.buscar_por_correo("pedro@ecotech.cl")
        cuenta = registrar_usuario("pedro_s", "Pedro2026!", pedro.id)
        self.assertEqual(cuenta.rol, "empleado")                   # menor permiso por defecto
        with self.assertRaises(ValueError):
            registrar_usuario("pedro_s", "Pedro2026!", pedro.id)   # usuario y empleado repetidos
        marta = EmpleadoDAO.buscar_por_correo("marta@ecotech.cl")
        with self.assertRaises(ValueError):
            registrar_usuario("pedro_s", "Otra2026!", marta.id)    # usuario repetido
        with self.assertRaises(ValueError):
            registrar_usuario("otro_usr", "Otra2026!", pedro.id)   # empleado repetido
        with self.assertRaises(ValueError):
            registrar_usuario("sin_emp", "Otra2026!", 9999)        # empleado inexistente
        with self.assertRaises(ValueError):
            registrar_usuario("clave_c", "123", marta.id)          # clave corta
        self.assertEqual(self.contar("usuario"), 4)

    def test_fallo_de_bd_no_da_acceso(self):
        with mock.patch.object(UsuarioDAO, "buscar_por_nombre", side_effect=ErrorBD("caída")):
            with self.assertRaises(ErrorBD):
                autenticar("admin", "Admin2026!")
            with mock.patch("builtins.input", return_value="admin"), \
                 mock.patch.object(menu_usuario, "getpass", return_value="Admin2026!"):
                self.assertIsNone(menu_usuario.solicitar_login())

    def test_login_menu(self):
        with mock.patch("builtins.input", return_value="admin"), \
             mock.patch.object(menu_usuario, "getpass", return_value="Admin2026!"):
            self.assertEqual(menu_usuario.solicitar_login().rol, "admin")
        with mock.patch("builtins.input", return_value="admin"), \
             mock.patch.object(menu_usuario, "getpass", return_value="mala"):
            self.assertIsNone(menu_usuario.solicitar_login())


class TestPermisos(Base):
    def test_sin_sesion(self):
        for sesion in (None, "admin", 5):
            with self.assertRaises(PermissionError):
                exigir_sesion(sesion)

    def test_empleado_no_es_admin(self):
        exigir_sesion(self.ana)
        exigir_admin(self.admin)
        with self.assertRaises(PermissionError):
            exigir_admin(self.ana)

    def test_empleado_no_puede_acciones_administrativas(self):
        antes = self.contar("empleado")
        with self.assertRaises(PermissionError):
            srv.registrar_empleado(self.ana, "intruso", "intruso@ecotech.cl")
        with self.assertRaises(PermissionError):
            srv.eliminar_empleado(self.ana, 1)
        with self.assertRaises(PermissionError):
            srv.datos_para_reportes(self.ana, 1)
        self.assertEqual(self.contar("empleado"), antes)

    def test_mi_ficha_usa_la_sesion(self):
        ficha = srv.consultar_mi_ficha(self.ana)
        self.assertEqual(ficha.correo, "ana@ecotech.cl")
        self.assertEqual(ficha.departamento.nombre, "Soporte")
        with self.assertRaises(PermissionError):
            srv.consultar_mi_ficha(None)

    def test_opcion_oculta_escrita_a_mano_es_rechazada(self):
        with mock.patch("builtins.input", side_effect=["5", "0"]), \
             mock.patch("builtins.print") as imprimir:
            menu_empleados.menu_empleados(self.ana)
        textos = " ".join(str(c.args[0]) for c in imprimir.call_args_list if c.args)
        self.assertIn("Permiso denegado", textos)
        self.assertNotIn("Eliminar empleado", textos)    # ni siquiera se mostró


class TestIndicadores(Base):
    def test_extraer_primero(self):
        i = api_indicadores.extraer_primero(JSON_UF, "uf")
        self.assertEqual((i.codigo, i.fecha, i.valor), ("uf", "2026-01-05", 40000.0))
        for malo in (None, [], {}, {"codigo": "uf", "serie": []},
                     {"codigo": "uf", "serie": [{"fecha": "x", "valor": 1}]},
                     {"codigo": "dolar", "serie": JSON_UF["serie"]}):
            with self.assertRaises(ValueError):
                api_indicadores.extraer_primero(malo, "uf")

    def test_extraer_primero_otros_formatos(self):
        """El adaptador tolera envoltorios distintos de la API real."""
        obs = {"date": "2026-01-05T03:00:00.000Z", "value": 40000.5}
        formatos = [
            {"status": "success", "data": {"code": "uf", "series": [obs]}},
            {"status": "success", "data": [{"code": "dolar", "value": 900.0, "date": "2026-01-05"},
                                           {"code": "uf", "series": [obs]}]},
            {"uf": {"code": "uf", "series": [obs]}, "dolar": {"code": "dolar", "series": [obs]}},
            {"data": {"code": "uf", "value": 40000.5, "date": "2026-01-05"}},
        ]
        for datos in formatos:
            i = api_indicadores.extraer_primero(datos, "uf")
            self.assertEqual((i.codigo, i.fecha), ("uf", "2026-01-05"))
        with self.assertRaises(ValueError):
            api_indicadores.extraer_primero({"data": [{"code": "dolar", "value": 1, "date": "2026-01-05"}]}, "uf")
        with self.assertRaises(ValueError):
            api_indicadores.extraer_primero("texto", "uf")

    def test_empleado_no_actualiza(self):
        with mock.patch("requests.get") as get:
            with self.assertRaises(PermissionError):
                actualizar_uf(self.ana)
            get.assert_not_called()                       # ni siquiera consultó la API
        self.assertEqual(self.contar("indicador"), 0)     # ninguna escritura

    def test_admin_actualiza_y_se_consulta_localmente(self):
        with mock.patch("requests.get", return_value=_respuesta(JSON_UF)) as get:
            indicador, origen = actualizar_uf(self.admin)
            self.assertEqual(get.call_args.kwargs["timeout"], (3, 5))
        self.assertEqual(origen, "api")
        guardado = consultar_guardado(self.ana, "uf")          # empleado consulta sin Internet
        self.assertEqual((guardado.fecha, guardado.valor), ("2026-01-05", 40000.0))

    def test_falla_externa_usa_respaldo(self):
        with mock.patch("requests.get", return_value=_respuesta(JSON_UF)):
            actualizar_uf(self.admin)
        for falla in (requests.ConnectionError("sin red"), requests.Timeout("lento")):
            with mock.patch("requests.get", side_effect=falla):
                indicador, origen = actualizar_uf(self.admin)
            self.assertEqual(origen, "respaldo")
            self.assertEqual(indicador.fecha, "2026-01-05")     # conserva su fecha original
        malo = _respuesta(None)
        malo.json.side_effect = ValueError("no es JSON")
        with mock.patch("requests.get", return_value=malo):
            self.assertEqual(actualizar_uf(self.admin)[1], "respaldo")
        http = _respuesta(None)
        http.raise_for_status.side_effect = requests.HTTPError("500")
        with mock.patch("requests.get", return_value=http):
            self.assertEqual(actualizar_uf(self.admin)[1], "respaldo")

    def test_falla_externa_sin_respaldo(self):
        with mock.patch("requests.get", side_effect=requests.ConnectionError("sin red")):
            self.assertEqual(actualizar_uf(self.admin), (None, "respaldo"))
        self.assertIsNone(consultar_guardado(self.admin, "uf"))

    def test_una_fila_por_codigo_y_fecha(self):
        IndicadorDAO.guardar(Indicador("uf", "2026-02-01", 100.0))
        IndicadorDAO.guardar(Indicador("uf", "2026-02-01", 100.0))
        self.assertEqual(IndicadorDAO.contar("uf", "2026-02-01"), 1)
        IndicadorDAO.guardar(Indicador("uf", "2026-02-01", 123.5))   # cambia el valor
        self.assertEqual(IndicadorDAO.contar("uf", "2026-02-01"), 1)
        self.assertEqual(IndicadorDAO.ultimo("uf").valor, 123.5)     # política: se actualiza
        IndicadorDAO.guardar(Indicador("dolar", "2026-02-01", 900.0))
        self.assertEqual(self.contar("indicador"), 2)               # otro código = otra fila


if __name__ == "__main__":
    unittest.main(verbosity=2)
