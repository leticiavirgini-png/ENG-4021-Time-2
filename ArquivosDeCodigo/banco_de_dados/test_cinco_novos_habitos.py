from datetime import date

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Cuidado, HistoricoFamiliar, Perfil, Usuario


class TestesCincoNovosHabitos(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Pessoa Teste', email='habitos-novos@medmap.com', senha='teste'
        )
        sessao = self.client.session
        sessao['usuario_id'] = self.usuario.id
        sessao.save()
        self.formulario = {
            'nome': 'Pessoa Teste',
            'data_nascimento': '2000-03-20',
            'sexo': 'Feminino',
        }

    def salvar(self, **habitos):
        dados = dict(self.formulario)
        dados.update(habitos)
        return self.client.post(reverse('PerfilSaude'), dados)

    def test_campos_começam_desmarcados(self):
        self.salvar()
        perfil = Perfil.objects.get(usuario=self.usuario)
        for campo in ('acima_peso', 'pouca_fruta', 'dorme_pouco',
                      'sol_sem_protetor', 'sem_dentista'):
            self.assertFalse(getattr(perfil, campo))

    def test_salvar_atualizar_e_desmarcar_habitos(self):
        self.salvar(acima_peso='sim', pouca_fruta='sim', dorme_pouco='sim',
                    sol_sem_protetor='sim', sem_dentista='sim', sedentario='sim')
        perfil = Perfil.objects.get(usuario=self.usuario)
        for campo in ('acima_peso', 'pouca_fruta', 'dorme_pouco',
                      'sol_sem_protetor', 'sem_dentista'):
            self.assertTrue(getattr(perfil, campo))
        self.salvar(dorme_pouco='sim')
        perfil.refresh_from_db()
        self.assertTrue(perfil.dorme_pouco)
        self.assertFalse(perfil.sol_sem_protetor)
        self.assertFalse(perfil.acima_peso)

    def test_cada_habito_gera_sua_recomendacao(self):
        self.salvar(acima_peso='sim', pouca_fruta='sim', dorme_pouco='sim',
                    sol_sem_protetor='sim', sem_dentista='sim')
        resposta = self.client.get(reverse('CheckupInteligente'))
        recomendacoes = resposta.context['recomendacoes']
        textos = [r['texto'] for r in recomendacoes]
        for trecho in ('Unidade Básica de Saúde', 'frutas, verduras e legumes',
                       '7 a 9 horas', 'FPS 30', 'pintas que mudam',
                       'dentista pelo menos uma vez'):
            self.assertTrue(any(trecho in texto for texto in textos), trecho)
        dentista = [r for r in recomendacoes if r['nome'] == 'Consulta com dentista']
        self.assertEqual(len(dentista), 1)
        self.assertEqual(dentista[0]['tipo'], 'Consulta')

    def test_risco_diabetes_sobrepeso_sedentarismo_sem_historico(self):
        self.salvar(acima_peso='sim', sedentario='sim')
        resposta = self.client.get(reverse('CheckupInteligente'))
        diabetes = [r for r in resposta.context['recomendacoes']
                    if r['nome'] == 'Glicemia de jejum']
        self.assertEqual(len(diabetes), 1)
        self.assertIn('repetir a cada 3 anos', diabetes[0]['texto'])
        self.assertNotIn('diabetes na família', diabetes[0]['texto'])

    def test_regra_diabetes_familiar_mantém_texto_anterior(self):
        self.salvar()
        perfil = Perfil.objects.get(usuario=self.usuario)
        HistoricoFamiliar.objects.create(perfil=perfil, parente='Pai',
                                         doenca='Diabetes tipo 2')
        resposta = self.client.get(reverse('CheckupInteligente'))
        diabetes = [r for r in resposta.context['recomendacoes']
                    if r['nome'] == 'Glicemia de jejum']
        self.assertEqual(len(diabetes), 1)
        self.assertIn('porque há diabetes na família', diabetes[0]['texto'])

    def test_nenhum_habito_marcado_mostra_mensagem(self):
        self.salvar()
        resposta = self.client.get(reverse('CheckupInteligente'))
        self.assertContains(resposta, 'Nenhum hábito de risco informado.')

    def test_consulta_dentista_pode_ir_para_o_calendario(self):
        self.salvar(sem_dentista='sim')
        resposta = self.client.post(reverse('CheckupInteligente'), {
            'nome': 'Consulta com dentista',
            'tipo': 'Consulta',
        })
        self.assertEqual(resposta.status_code, 302)
        perfil = Perfil.objects.get(usuario=self.usuario)
        self.assertTrue(Cuidado.objects.filter(
            perfil=perfil, nome='Consulta com dentista', tipo='Consulta'
        ).exists())
