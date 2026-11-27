from datetime import date

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Cuidado, HistoricoFamiliar, Perfil, Usuario


class TestesFiltrosCalendario(TestCase):
    @classmethod
    def setUpTestData(cls):
        usuario = Usuario.objects.create(
            nome='Pessoa Teste', email='teste-filtros@medmap.com', senha='teste'
        )
        perfil = Perfil.objects.create(
            usuario=usuario, nome='Pessoa Teste',
            data_nascimento=date(1998, 5, 10), sexo='Não informado'
        )
        exemplos = [
            ('Consulta', 'Consulta A', date(2026, 11, 10)),
            ('Exame', 'Exame B', date(2026, 11, 14)),
            ('Consulta', 'Consulta C', date(2026, 12, 10)),
            ('Vacina', 'Vacina D', date(2026, 12, 20)),
        ]
        for tipo, nome, dia in exemplos:
            Cuidado.objects.create(perfil=perfil, tipo=tipo, nome=nome, data=dia)

    def nomes(self, resposta):
        return [c.nome for c in resposta.context['cuidados']]

    def test_exibe_todos_ordenados_por_data(self):
        resposta = self.client.get(reverse('CalendarioCuidados'))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self.nomes(resposta),
                         ['Consulta A', 'Exame B', 'Consulta C', 'Vacina D'])

    def test_filtra_pelo_tipo(self):
        resposta = self.client.get(reverse('CalendarioCuidados'),
                                  {'tipo': 'Exame'})
        self.assertEqual(self.nomes(resposta), ['Exame B'])

    def test_filtra_tipo_e_intervalo_de_datas(self):
        resposta = self.client.get(reverse('CalendarioCuidados'), {
            'tipo': 'Consulta', 'inicio': '2026-11-15', 'fim': '2026-12-31'
        })
        self.assertEqual(self.nomes(resposta), ['Consulta C'])

    def test_ordena_do_mais_recente_ao_mais_antigo(self):
        resposta = self.client.get(reverse('CalendarioCuidados'),
                                  {'ordem': 'desc'})
        self.assertEqual(self.nomes(resposta),
                         ['Vacina D', 'Consulta C', 'Exame B', 'Consulta A'])

    def test_intervalo_invertido_exibe_erro_e_lista_vazia(self):
        resposta = self.client.get(reverse('CalendarioCuidados'), {
            'inicio': '2026-12-31', 'fim': '2026-11-01'
        })
        self.assertEqual(self.nomes(resposta), [])
        self.assertContains(resposta, 'data inicial deve ser anterior')

    def test_tipo_invalido_nao_gera_erro(self):
        resposta = self.client.get(reverse('CalendarioCuidados'),
                                  {'tipo': 'Outro', 'ordem': 'outro'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(self.nomes(resposta)), 4)

    def test_sem_resultados_mostra_mensagem(self):
        resposta = self.client.get(reverse('CalendarioCuidados'), {
            'inicio': '2027-01-01'
        })
        self.assertEqual(self.nomes(resposta), [])
        self.assertContains(resposta, '0 cuidado(s) encontrado(s).')

    def test_data_invalida_nao_quebra_a_pagina(self):
        resposta = self.client.get(reverse('CalendarioCuidados'),
                                  {'inicio': '2026-02-30'})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'data inicial informada')
