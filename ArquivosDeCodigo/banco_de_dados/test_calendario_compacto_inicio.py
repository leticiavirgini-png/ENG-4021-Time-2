from datetime import date

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Cuidado, Perfil, Usuario


class TestesCalendarioCompactoInicio(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(nome='Pessoa', email='mini@teste.com', senha='teste')
        self.perfil = Perfil.objects.create(usuario=self.usuario, nome='Pessoa',
                                           data_nascimento=date(2000, 1, 1), sexo='Outro')
        sessao = self.client.session
        sessao['usuario_id'] = self.usuario.id
        sessao.save()

    def test_novo_card_preserva_os_quatro_anteriores(self):
        resposta = self.client.get(reverse('InicioLogado'), {'mes': '2026-11'})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Calendário')
        self.assertEqual(resposta.content.count(b'class="area-card '), 5)

    def test_destaca_somente_datas_do_usuario(self):
        Cuidado.objects.create(perfil=self.perfil, nome='Consulta', tipo='Consulta',
                               data=date(2026, 11, 18))
        outro = Usuario.objects.create(nome='Outro', email='outro-mini@teste.com', senha='teste')
        perfil = Perfil.objects.create(usuario=outro, nome='Outro',
                                      data_nascimento=date(2001, 1, 1), sexo='Outro')
        Cuidado.objects.create(perfil=perfil, nome='Vacina', tipo='Vacina',
                               data=date(2026, 11, 22))
        resposta = self.client.get(reverse('InicioLogado'), {'mes': '2026-11'})
        self.assertContains(resposta, 'data-cuidado="2026-11-18"')
        self.assertNotContains(resposta, 'data-cuidado="2026-11-22"')

    def test_mes_invalido_nao_quebra_a_pagina(self):
        resposta = self.client.get(reverse('InicioLogado'), {'mes': '9999-77'})
        self.assertEqual(resposta.status_code, 200)

    def test_dia_abre_calendario_filtrado(self):
        resposta = self.client.get(reverse('InicioLogado'), {'mes': '2026-11'})
        self.assertContains(resposta, 'inicio=2026-11-18&amp;fim=2026-11-18', html=False)
