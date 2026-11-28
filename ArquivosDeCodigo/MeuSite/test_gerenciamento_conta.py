from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Usuario


class BaseConta(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Thiago', email='thiago@teste.com', senha=make_password('senha123')
        )
        self.outro = Usuario.objects.create(
            nome='Outra Pessoa', email='outra@teste.com', senha=make_password('outra123')
        )

    def entrar(self, usuario, contas=None):
        sessao = self.client.session
        sessao['usuario_id'] = usuario.id
        sessao['contas_utilizadas'] = contas if contas is not None else [usuario.id]
        sessao.save()


class TestesMinhaConta(BaseConta):
    def test_sem_login_vai_para_o_login(self):
        resposta = self.client.get(reverse('MinhaConta'))
        self.assertRedirects(resposta, reverse('Tela'))

    def test_mostra_os_dados_da_conta(self):
        self.entrar(self.usuario)
        resposta = self.client.get(reverse('MinhaConta'))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context['usuario'], self.usuario)


class TestesEdicaoUsuario(BaseConta):
    def url(self, usuario=None):
        return reverse('EdicaoUsuario', args=[(usuario or self.usuario).id])

    def test_sem_login_vai_para_o_login(self):
        resposta = self.client.get(self.url())
        self.assertRedirects(resposta, reverse('Tela'))

    def test_nao_pode_editar_a_conta_de_outra_pessoa(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(self.outro), {
            'nome': 'Invasor', 'email': 'invasor@teste.com', 'senha': ''
        })
        self.assertRedirects(resposta, reverse('InicioLogado'))
        self.outro.refresh_from_db()
        self.assertEqual(self.outro.nome, 'Outra Pessoa')

    def test_edita_nome_e_email(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), {
            'nome': '  Thiago Braz ', 'email': ' Novo@Teste.com ', 'senha': ''
        })
        self.assertRedirects(resposta, reverse('InicioLogado'))
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome, 'Thiago Braz')
        self.assertEqual(self.usuario.email, 'novo@teste.com')
        # sem nova senha, a senha antiga continua valendo
        self.assertTrue(check_password('senha123', self.usuario.senha))

    def test_troca_a_senha(self):
        self.entrar(self.usuario)
        self.client.post(self.url(), {
            'nome': 'Thiago', 'email': 'thiago@teste.com', 'senha': 'novasenha'
        })
        self.usuario.refresh_from_db()
        self.assertTrue(check_password('novasenha', self.usuario.senha))

    def test_rejeita_senha_curta(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), {
            'nome': 'Thiago', 'email': 'thiago@teste.com', 'senha': '123'
        })
        self.assertContains(resposta, 'pelo menos 6 caracteres')
        self.usuario.refresh_from_db()
        self.assertTrue(check_password('senha123', self.usuario.senha))

    def test_rejeita_email_de_outra_conta(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), {
            'nome': 'Thiago', 'email': 'outra@teste.com', 'senha': ''
        })
        self.assertContains(resposta, 'Este e-mail já está sendo utilizado.')
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.email, 'thiago@teste.com')

    def test_rejeita_nome_vazio(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), {
            'nome': '   ', 'email': 'thiago@teste.com', 'senha': ''
        })
        self.assertContains(resposta, 'Nome e e-mail são obrigatórios.')
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome, 'Thiago')


class TestesRemocaoUsuario(BaseConta):
    def url(self, usuario=None):
        return reverse('RemocaoUsuario', args=[(usuario or self.usuario).id])

    def dados(self, **extra):
        dados = {'email': 'thiago@teste.com', 'senha': 'senha123', 'confirmacao': 'sim'}
        dados.update(extra)
        return dados

    def test_sem_login_vai_para_o_login(self):
        resposta = self.client.get(self.url())
        self.assertRedirects(resposta, reverse('Tela'))

    def test_nao_pode_excluir_a_conta_de_outra_pessoa(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(self.outro), {
            'email': 'outra@teste.com', 'senha': 'outra123', 'confirmacao': 'sim'
        })
        self.assertRedirects(resposta, reverse('InicioLogado'))
        self.assertTrue(Usuario.objects.filter(id=self.outro.id).exists())

    def test_email_errado_nao_exclui(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), self.dados(email='errado@teste.com'))
        self.assertContains(resposta, 'O e-mail informado não corresponde à conta.')
        self.assertTrue(Usuario.objects.filter(id=self.usuario.id).exists())

    def test_senha_errada_nao_exclui(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), self.dados(senha='errada'))
        self.assertContains(resposta, 'Senha incorreta.')
        self.assertTrue(Usuario.objects.filter(id=self.usuario.id).exists())

    def test_sem_confirmacao_nao_exclui(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), self.dados(confirmacao=''))
        self.assertContains(resposta, 'Você precisa confirmar a exclusão.')
        self.assertTrue(Usuario.objects.filter(id=self.usuario.id).exists())

    def test_exclui_a_conta_e_encerra_a_sessao(self):
        self.entrar(self.usuario)
        resposta = self.client.post(self.url(), self.dados())
        self.assertRedirects(resposta, reverse('home'))
        self.assertFalse(Usuario.objects.filter(id=self.usuario.id).exists())
        self.assertNotIn('usuario_id', self.client.session)


class TestesTrocarConta(BaseConta):
    def test_sem_login_vai_para_o_login(self):
        resposta = self.client.post(reverse('TrocarConta'), {'conta_id': self.outro.id})
        self.assertRedirects(resposta, reverse('Tela'))

    def test_get_volta_para_o_inicio(self):
        self.entrar(self.usuario)
        resposta = self.client.get(reverse('TrocarConta'))
        self.assertRedirects(resposta, reverse('InicioLogado'))

    def test_troca_para_conta_usada_com_a_senha_certa(self):
        self.entrar(self.usuario, contas=[self.usuario.id, self.outro.id])
        resposta = self.client.post(reverse('TrocarConta'), {
            'conta_id': self.outro.id, 'senha': 'outra123'
        })
        self.assertRedirects(resposta, reverse('InicioLogado'))
        self.assertEqual(self.client.session['usuario_id'], self.outro.id)

    def test_senha_errada_nao_troca(self):
        self.entrar(self.usuario, contas=[self.usuario.id, self.outro.id])
        resposta = self.client.post(reverse('TrocarConta'), {
            'conta_id': self.outro.id, 'senha': 'errada'
        })
        self.assertContains(resposta, 'Senha incorreta')
        self.assertEqual(self.client.session['usuario_id'], self.usuario.id)

    def test_nao_troca_para_conta_que_nao_foi_usada_neste_navegador(self):
        self.entrar(self.usuario, contas=[self.usuario.id])
        resposta = self.client.post(reverse('TrocarConta'), {
            'conta_id': self.outro.id, 'senha': 'outra123'
        })
        self.assertRedirects(resposta, reverse('InicioLogado'))
        self.assertEqual(self.client.session['usuario_id'], self.usuario.id)

    def test_conta_invalida_nao_gera_erro(self):
        self.entrar(self.usuario)
        resposta = self.client.post(reverse('TrocarConta'), {'conta_id': 'abc', 'senha': 'x'})
        self.assertRedirects(resposta, reverse('InicioLogado'))


class TestesSair(BaseConta):
    def test_sair_encerra_a_sessao_mas_lembra_as_contas_usadas(self):
        self.entrar(self.usuario, contas=[self.usuario.id, self.outro.id])
        resposta = self.client.get(reverse('Sair'))
        self.assertRedirects(resposta, reverse('home'))
        self.assertNotIn('usuario_id', self.client.session)
        self.assertEqual(
            self.client.session['contas_utilizadas'], [self.usuario.id, self.outro.id]
        )

    def test_depois_de_sair_nao_acessa_a_conta(self):
        self.entrar(self.usuario)
        self.client.get(reverse('Sair'))
        resposta = self.client.get(reverse('MinhaConta'))
        self.assertRedirects(resposta, reverse('Tela'))
