from datetime import datetime, timedelta, timezone
import pytest
from servicios.validaciones import clave_valida, correo_valido, estado_login, centesimas, suma_valida
from servicios.calificar import calcular_nota

@pytest.mark.parametrize('clave,esperado',[('Abcdef1!',True),('Abcde1!',False),('abcdef1!',False),('Abcdefg!',False),('Abcdef12',False),('',False)])
def test_uni01_claves(clave,esperado): assert clave_valida(clave) is esperado

@pytest.mark.parametrize('correo,esperado',[('laura@example.com',True),('laura@',False),('laura.com',False),('',False),('a b@c.com',False)])
def test_uni01_correo(correo,esperado): assert correo_valido(correo) is esperado

@pytest.mark.parametrize('respuestas,nota',[({1:11,2:21,3:31},500),({1:11,2:22},200),({},0),({1:99},0)])
def test_uni02_nota(respuestas,nota):
    assert calcular_nota([{'id':1,'puntaje':200,'correcta':11},{'id':2,'puntaje':200,'correcta':21},{'id':3,'puntaje':100,'correcta':31}],respuestas)==nota

@pytest.mark.parametrize('valores,valido',[(['2','2','1'],True),(['1,7','1,7','1,6'],True),(['2','2','0,5'],False),(['2','2','1,5'],False)])
def test_uni02_suma(valores,valido): assert suma_valida(centesimas(v) for v in valores) is valido

def test_uni03_bloqueo():
    ahora=datetime(2026,11,16,tzinfo=timezone.utc)
    intentos=0
    for i in range(4):
        ok,intentos,hasta,_=estado_login(1,intentos,None,False,ahora)
        assert not ok and hasta is None and intentos==i+1
    ok,intentos,hasta,_=estado_login(1,intentos,None,False,ahora)
    assert not ok and datetime.fromisoformat(hasta)==ahora+timedelta(minutes=15)
    assert not estado_login(1,intentos,hasta,True,ahora+timedelta(minutes=14))[0]
    assert estado_login(1,intentos,hasta,True,ahora+timedelta(minutes=15))[:3]==(True,0,None)
    assert not estado_login(0,0,None,True,ahora)[0]
