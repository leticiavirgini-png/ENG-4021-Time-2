from datetime import date

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import HistoricoFamiliar, Perfil, Usuario


class TestesQuatroDoencasHistorico(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Pessoa Teste', email='novas-doencas@medmap.com', senha='teste'
        )
        self.perfil = Perfil.objects.create(
            usuario=self.usuario, nome='Pessoa Teste',
            data_nascimento=date(1980, 4, 20), sexo='Masculino'
        )
        sessao = self.client.session
        sessao['usuario_id'] = self.usuario.id
        sessao.save()

    def historico(self, doenca, parente='Pai'):
        return HistoricoFamiliar.objects.create(
            perfil=self.perfil, doenca=doenca, parente=parente,
            idade_diagnostico=50
        )

    def recomendacoes(self):
        resposta = self.client.get(reverse('CheckupInteligente'))
        self.assertEqual(resposta.status_code, 200)
        return resposta.context['recomendacoes']

    def test_quatro_doencas_aparecem_na_lista(self):
        resposta = self.client.get(reverse('HistoricoFamiliar'))
        self.assertEqual(resposta.status_code, 200)
        for nome in ('Câncer de pele (melanoma)', 'Glaucoma',
                     'Câncer de ovário', 'Doença renal crônica'):
            self.assertContains(resposta, 'value="' + nome + '"')

    def test_melanoma_recomenda_dermatologista(self):
        self.historico('Câncer de pele (melanoma)')
        regras = [r for r in self.recomendacoes()
                  if r['nome'] == 'Consulta com dermatologista']
        self.assertEqual(len(regras), 1)
        self.assertEqual(regras[0]['tipo'], 'Consulta')
        self.assertIn('uma vez por ano', regras[0]['texto'])

    def test_glaucoma_a_partir_dos_40(self):
        self.historico('Glaucoma')
        regras = [r for r in self.recomendacoes()
                  if r['nome'] == 'Exame de glaucoma']
        self.assertEqual(len(regras), 1)
        self.assertEqual(regras[0]['tipo'], 'Exame')
        self.assertIn('pressão ocular', regras[0]['texto'])

    def test_glaucoma_antes_dos_40_nao_gera_regra(self):
        self.perfil.data_nascimento = date(2000, 1, 1)
        self.perfil.save()
        self.historico('Glaucoma')
        self.assertFalse(any(r['nome'] == 'Exame de glaucoma'
                             for r in self.recomendacoes()))

    def test_cancer_de_ovario_recomenda_independente_do_sexo(self):
        self.historico('Câncer de ovário')
        regras = [r for r in self.recomendacoes()
                  if r['nome'] == 'Consulta sobre aconselhamento genético']
        self.assertEqual(len(regras), 1)
        self.assertEqual(regras[0]['tipo'], 'Consulta')
        self.assertIn('risco hereditário', regras[0]['texto'])

    def test_doenca_renal_recomenda_exames(self):
        self.historico('Doença renal crônica')
        regras = [r for r in self.recomendacoes()
                  if r['nome'] == 'Exame dos rins']
        self.assertEqual(len(regras), 1)
        self.assertEqual(regras[0]['tipo'], 'Exame')
        self.assertIn('creatinina no sangue', regras[0]['texto'])

    def test_parente_distante_nao_gera_recomendacao(self):
        for doenca in ('Câncer de pele (melanoma)', 'Glaucoma',
                       'Câncer de ovário', 'Doença renal crônica'):
            self.historico(doenca, parente='Avó materna')
        nomes = {r['nome'] for r in self.recomendacoes()}
        for nome in ('Consulta com dermatologista', 'Exame de glaucoma',
                     'Consulta sobre aconselhamento genético', 'Exame dos rins'):
            self.assertNotIn(nome, nomes)

    def test_registro_no_historico_pode_ser_salvo_pelo_formulario(self):
        resposta = self.client.post(reverse('HistoricoFamiliar'), {
            'parente': 'Mãe',
            'doenca': 'Câncer de ovário',
            'idade': '49',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(HistoricoFamiliar.objects.filter(
            perfil=self.perfil, parente='Mãe', doenca='Câncer de ovário'
        ).exists())
