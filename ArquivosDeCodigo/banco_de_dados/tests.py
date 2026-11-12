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



class TestesEdicaoRelatorioPreventivo(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Usuário Relatório',
            email='relatorio@medmap.com',
            senha='teste'
        )
        self.perfil = Perfil.objects.create(
            usuario=self.usuario,
            nome='Usuário Relatório',
            data_nascimento=date(1990, 1, 1),
            sexo='Não informado'
        )
        self.historico = HistoricoFamiliar.objects.create(
            perfil=self.perfil,
            parente='Pai',
            doenca='Hipertensão',
            idade_diagnostico=45
        )
        self.cuidado = Cuidado.objects.create(
            perfil=self.perfil,
            tipo='Consulta',
            nome='Clínico geral',
            data=date(2026, 11, 10)
        )
        sessao = self.client.session
        sessao['usuario_id'] = self.usuario.id
        sessao.save()

    def test_edita_historico_familiar(self):
        resposta = self.client.post(reverse('RelatorioPreventivo'), {
            'acao': 'editar_historico',
            'historico_id': self.historico.id,
            'parente': 'Mãe',
            'doenca': 'Diabetes',
            'idade_diagnostico': '50'
        })

        self.historico.refresh_from_db()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self.historico.parente, 'Mãe')
        self.assertEqual(self.historico.doenca, 'Diabetes')
        self.assertEqual(self.historico.idade_diagnostico, 50)
        self.assertContains(resposta, 'Histórico familiar atualizado')

    def test_adiciona_historico_familiar_pelo_relatorio(self):
        resposta = self.client.post(reverse('RelatorioPreventivo'), {
            'acao': 'adicionar_historico',
            'parente': 'Avó materna',
            'doenca': 'Diabetes',
            'idade_diagnostico': '60'
        })

        novo = HistoricoFamiliar.objects.get(
            perfil=self.perfil,
            parente='Avó materna'
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(novo.doenca, 'Diabetes')
        self.assertContains(resposta, 'Histórico familiar adicionado')

    def test_edita_cuidado(self):
        resposta = self.client.post(reverse('RelatorioPreventivo'), {
            'acao': 'editar_cuidado',
            'cuidado_id': self.cuidado.id,
            'tipo': 'Exame',
            'nome': 'Hemograma',
            'data': '2026-12-01'
        })

        self.cuidado.refresh_from_db()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(self.cuidado.tipo, 'Exame')
        self.assertEqual(self.cuidado.nome, 'Hemograma')
        self.assertEqual(self.cuidado.data, date(2026, 12, 1))
        self.assertContains(resposta, 'Cuidado atualizado com sucesso')

    def test_adiciona_cuidado_pelo_relatorio(self):
        resposta = self.client.post(reverse('RelatorioPreventivo'), {
            'acao': 'adicionar_cuidado',
            'tipo': 'Vacina',
            'nome': 'Vacina da gripe',
            'data': '2026-11-20'
        })

        novo = Cuidado.objects.get(
            perfil=self.perfil,
            nome='Vacina da gripe'
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(novo.tipo, 'Vacina')
        self.assertContains(resposta, 'Cuidado adicionado com sucesso')

    def test_nao_edita_historico_de_outro_perfil(self):
        outro_usuario = Usuario.objects.create(
            nome='Outro Usuário',
            email='outro@medmap.com',
            senha='teste'
        )
        outro_perfil = Perfil.objects.create(
            usuario=outro_usuario,
            nome='Outro Usuário',
            data_nascimento=date(1985, 1, 1),
            sexo='Não informado'
        )
        historico_alheio = HistoricoFamiliar.objects.create(
            perfil=outro_perfil,
            parente='Pai',
            doenca='Asma'
        )

        resposta = self.client.post(reverse('RelatorioPreventivo'), {
            'acao': 'editar_historico',
            'historico_id': historico_alheio.id,
            'parente': 'Mãe',
            'doenca': 'Diabetes',
            'idade_diagnostico': '40'
        })

        historico_alheio.refresh_from_db()
        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(historico_alheio.doenca, 'Asma')
