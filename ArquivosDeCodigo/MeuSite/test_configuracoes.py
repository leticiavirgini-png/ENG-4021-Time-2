import json
import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

PASTA_PROJETO = Path(__file__).resolve().parent.parent


def ler_configuracoes(**variaveis):
    """Carrega o settings.py num processo separado, com as variáveis de ambiente informadas."""
    ambiente = {
        chave: valor for chave, valor in os.environ.items()
        if not chave.startswith('MEDMAP_')
    }
    ambiente.update(variaveis)
    codigo = (
        'import json\n'
        'from MeuSite import settings as s\n'
        'print(json.dumps({"secret_key": s.SECRET_KEY, "debug": s.DEBUG, '
        '"allowed_hosts": s.ALLOWED_HOSTS}))'
    )
    resultado = subprocess.run(
        [sys.executable, '-B', '-c', codigo],
        cwd=PASTA_PROJETO, env=ambiente,
        capture_output=True, text=True, check=True
    )
    return json.loads(resultado.stdout)


class TestesConfiguracoes(SimpleTestCase):
    def test_sem_variaveis_mantem_os_valores_de_desenvolvimento(self):
        config = ler_configuracoes()
        self.assertTrue(config['secret_key'].startswith('django-insecure-'))
        self.assertTrue(config['debug'])
        self.assertEqual(config['allowed_hosts'], ['*'])

    def test_le_a_chave_secreta_do_ambiente(self):
        config = ler_configuracoes(MEDMAP_SECRET_KEY='chave-de-producao')
        self.assertEqual(config['secret_key'], 'chave-de-producao')

    def test_desliga_o_debug(self):
        for valor in ('False', 'false', '0', 'nao'):
            config = ler_configuracoes(MEDMAP_DEBUG=valor)
            self.assertFalse(config['debug'], valor)

    def test_le_a_lista_de_enderecos_permitidos(self):
        config = ler_configuracoes(MEDMAP_ALLOWED_HOSTS='medmap.com, www.medmap.com,')
        self.assertEqual(config['allowed_hosts'], ['medmap.com', 'www.medmap.com'])
