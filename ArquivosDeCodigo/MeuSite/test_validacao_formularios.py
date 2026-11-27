from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Cuidado, HistoricoFamiliar, Perfil, Usuario


class BaseValidacao(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Pessoa', email='validacao@teste.com', senha='teste'
        )
        sessao = self.client.session
        sessao['usuario_id'] = self.usuario.id
        sessao.save()

    def criar_perfil(self):
        return Perfil.objects.create(
            usuario=self.usuario, nome='Pessoa',
            data_nascimento=date(1990, 1, 1), sexo='Feminino'
        )


class TestesValidacaoPerfil(BaseValidacao):
    def salvar(self, **dados):
        dados_completos = {'nome': 'Pessoa', 'data_nascimento': '1990-05-10', 'sexo': 'Feminino'}
        dados_completos.update(dados)
        return self.client.post(reverse('PerfilSaude'), dados_completos)

    def test_dados_corretos_continuam_funcionando(self):
        resposta = self.salvar()
        self.assertContains(resposta, 'Perfil salvo com sucesso.')
        self.assertEqual(Perfil.objects.get().data_nascimento, date(1990, 5, 10))

    def test_data_que_nao_existe_nao_derruba_o_site(self):
        resposta = self.salvar(data_nascimento='1990-02-31')
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Preencha todos os campos do perfil.')
        self.assertFalse(Perfil.objects.exists())

    def test_rejeita_data_de_nascimento_no_futuro(self):
        amanha = (date.today() + timedelta(days=1)).isoformat()
        resposta = self.salvar(data_nascimento=amanha)
        self.assertContains(resposta, 'não pode estar no futuro')
        self.assertFalse(Perfil.objects.exists())

    def test_rejeita_data_de_nascimento_muito_antiga(self):
        resposta = self.salvar(data_nascimento='1850-01-01')
        self.assertContains(resposta, 'Informe uma data de nascimento válida.')
        self.assertFalse(Perfil.objects.exists())

    def test_rejeita_nome_muito_grande(self):
        resposta = self.salvar(nome='a' * 101)
        self.assertContains(resposta, 'até 100 caracteres')
        self.assertFalse(Perfil.objects.exists())

    def test_rejeita_sexo_fora_das_opcoes(self):
        resposta = self.salvar(sexo='Qualquer coisa')
        self.assertContains(resposta, 'Selecione uma opção válida de sexo.')
        self.assertFalse(Perfil.objects.exists())

    def test_erro_nao_altera_o_perfil_ja_salvo(self):
        self.criar_perfil()
        self.salvar(nome='Outro nome', data_nascimento='2999-01-01')
        perfil = Perfil.objects.get()
        self.assertEqual(perfil.nome, 'Pessoa')
        self.assertEqual(perfil.data_nascimento, date(1990, 1, 1))


class TestesValidacaoHistorico(BaseValidacao):
    def setUp(self):
        super().setUp()
        self.criar_perfil()

    def adicionar(self, **dados):
        dados_completos = {'acao': 'adicionar', 'parente': 'Mãe', 'doenca': 'Diabetes tipo 2', 'idade': '50'}
        dados_completos.update(dados)
        return self.client.post(reverse('HistoricoFamiliar'), dados_completos)

    def test_dados_corretos_continuam_funcionando(self):
        resposta = self.adicionar()
        self.assertContains(resposta, 'Informação adicionada com sucesso.')
        self.assertEqual(HistoricoFamiliar.objects.count(), 1)

    def test_rejeita_parentesco_muito_grande(self):
        resposta = self.adicionar(parente='a' * 51)
        self.assertContains(resposta, 'ultrapassam o limite permitido')
        self.assertFalse(HistoricoFamiliar.objects.exists())

    def test_rejeita_doenca_muito_grande(self):
        resposta = self.adicionar(doenca='a' * 151)
        self.assertContains(resposta, 'ultrapassam o limite permitido')
        self.assertFalse(HistoricoFamiliar.objects.exists())


class TestesValidacaoCuidados(BaseValidacao):
    def setUp(self):
        super().setUp()
        self.criar_perfil()

    def cadastrar(self, **dados):
        dados_completos = {'tipo': 'Exame', 'nome': 'Hemograma', 'data': '2026-12-10'}
        dados_completos.update(dados)
        return self.client.post(reverse('CadastroCuidados'), dados_completos)

    def test_dados_corretos_continuam_funcionando(self):
        resposta = self.cadastrar()
        self.assertRedirects(resposta, reverse('InicioLogado'), fetch_redirect_response=False)
        self.assertEqual(Cuidado.objects.get().data, date(2026, 12, 10))

    def test_data_que_nao_existe_nao_derruba_o_site(self):
        resposta = self.cadastrar(data='2026-02-31')
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Informe uma data válida.')
        self.assertFalse(Cuidado.objects.exists())

    def test_rejeita_nome_muito_grande(self):
        resposta = self.cadastrar(nome='a' * 151)
        self.assertContains(resposta, 'até 150 caracteres')
        self.assertFalse(Cuidado.objects.exists())
