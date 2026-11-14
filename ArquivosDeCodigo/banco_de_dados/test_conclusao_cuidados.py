from datetime import date

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Cuidado, Perfil, Usuario


class TestesConclusaoCuidados(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(nome='Pessoa', email='pessoa@teste.com', senha='teste')
        self.perfil = Perfil.objects.create(
            usuario=self.usuario, nome='Pessoa', sexo='Não informado',
            data_nascimento=date(2000, 1, 1)
        )
        self.cuidado = Cuidado.objects.create(
            perfil=self.perfil, nome='Exame', tipo='Exame',
            data=date(2026, 11, 10)
        )
        sessao = self.client.session
        sessao['usuario_id'] = self.usuario.pk
        sessao.save()

    def test_concluir_sem_reagendar(self):
        resposta = self.client.post(reverse('AtualizarCuidado', args=[self.cuidado.pk]),
                                    {'acao': 'concluir', 'meses': '0'})
        self.cuidado.refresh_from_db()
        self.assertRedirects(resposta, reverse('CalendarioCuidados'))
        self.assertTrue(self.cuidado.concluido)
        self.assertEqual(Cuidado.objects.filter(perfil=self.perfil).count(), 1)

    def test_reagendar_cria_outro_cuidado(self):
        self.client.post(reverse('AtualizarCuidado', args=[self.cuidado.pk]),
                         {'acao': 'concluir', 'meses': '6'})
        self.assertEqual(Cuidado.objects.filter(perfil=self.perfil).count(), 2)
        novo = Cuidado.objects.exclude(pk=self.cuidado.pk).get()
        self.assertFalse(novo.concluido)
        self.assertEqual(novo.tipo, 'Exame')

    def test_repetir_confirmacao_nao_cria_duplicata(self):
        url = reverse('AtualizarCuidado', args=[self.cuidado.pk])
        self.client.post(url, {'acao': 'concluir', 'meses': '6'})
        self.client.post(url, {'acao': 'concluir', 'meses': '6'})
        self.assertEqual(Cuidado.objects.filter(perfil=self.perfil).count(), 2)

    def test_desfazer_conclusao(self):
        self.cuidado.concluido = True
        self.cuidado.save()
        self.client.post(reverse('AtualizarCuidado', args=[self.cuidado.pk]),
                         {'acao': 'desfazer'})
        self.cuidado.refresh_from_db()
        self.assertFalse(self.cuidado.concluido)

    def test_nao_altera_cuidado_de_outro_usuario(self):
        outro = Usuario.objects.create(nome='Outro', email='outro@teste.com', senha='teste')
        perfil = Perfil.objects.create(
            usuario=outro, nome='Outro', sexo='Não informado',
            data_nascimento=date(1990, 1, 1)
        )
        cuidado = Cuidado.objects.create(perfil=perfil, nome='Outro exame', tipo='Exame',
                                         data=date(2026, 11, 1))
        resposta = self.client.post(reverse('AtualizarCuidado', args=[cuidado.pk]),
                                    {'acao': 'concluir', 'meses': '0'})
        self.assertEqual(resposta.status_code, 404)
        cuidado.refresh_from_db()
        self.assertFalse(cuidado.concluido)
