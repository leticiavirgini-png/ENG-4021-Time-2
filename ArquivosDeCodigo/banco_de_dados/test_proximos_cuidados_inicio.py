from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Cuidado, Perfil, Usuario


class TestesProximosCuidadosInicio(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(nome='Pessoa', email='inicio@teste.com', senha='teste')
        self.perfil = Perfil.objects.create(usuario=self.usuario, nome='Pessoa',
                                           data_nascimento=date(2000, 1, 1), sexo='Outro')
        sessao = self.client.session
        sessao['usuario_id'] = self.usuario.pk
        sessao.save()

    def test_exibe_apenas_tres_proximos_na_ordem(self):
        hoje = date.today()
        for dias in (4, 1, 3, 2):
            Cuidado.objects.create(perfil=self.perfil, nome=f'Cuidado {dias}',
                                   tipo='Consulta', data=hoje + timedelta(days=dias))
        resposta = self.client.get(reverse('InicioLogado'))
        nomes = [c.nome for c in resposta.context['proximos_cuidados']]
        self.assertEqual(nomes, ['Cuidado 1', 'Cuidado 2', 'Cuidado 3'])

    def test_nao_mostra_cuidados_concluidos_ou_passados(self):
        hoje = date.today()
        Cuidado.objects.create(perfil=self.perfil, nome='Concluído',
                               tipo='Exame', data=hoje, concluido=True)
        Cuidado.objects.create(perfil=self.perfil, nome='Passado',
                               tipo='Exame', data=hoje - timedelta(days=1))
        resposta = self.client.get(reverse('InicioLogado'))
        self.assertEqual(list(resposta.context['proximos_cuidados']), [])

    def test_nao_exibe_cuidados_de_outro_perfil(self):
        outro = Usuario.objects.create(nome='Outra', email='outra@teste.com', senha='teste')
        perfil = Perfil.objects.create(usuario=outro, nome='Outra',
                                      data_nascimento=date(1998, 1, 1), sexo='Outro')
        Cuidado.objects.create(perfil=perfil, nome='Consulta privada',
                               tipo='Consulta', data=date.today())
        resposta = self.client.get(reverse('InicioLogado'))
        self.assertNotContains(resposta, 'Consulta privada')
