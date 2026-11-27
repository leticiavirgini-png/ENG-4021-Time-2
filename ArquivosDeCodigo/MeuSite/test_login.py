from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Usuario


class TestesLogin(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome='Thiago', email='thiago@teste.com', senha=make_password('senha123')
        )
        self.url = reverse('Tela')

    def entrar(self, email, senha='senha123'):
        return self.client.post(self.url, {'email': email, 'senha': senha})

    def test_pagina_de_login_abre(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)

    def test_login_com_dados_corretos(self):
        resposta = self.entrar('thiago@teste.com')
        self.assertRedirects(resposta, reverse('InicioLogado'))
        self.assertEqual(self.client.session['usuario_id'], self.usuario.id)

    def test_login_com_email_em_maiusculas(self):
        resposta = self.entrar('Thiago@Teste.COM')
        self.assertRedirects(resposta, reverse('InicioLogado'))
        self.assertEqual(self.client.session['usuario_id'], self.usuario.id)

    def test_login_com_espacos_no_email(self):
        resposta = self.entrar('  thiago@teste.com  ')
        self.assertRedirects(resposta, reverse('InicioLogado'))

    def test_senha_errada(self):
        resposta = self.entrar('thiago@teste.com', 'senhaerrada')
        self.assertContains(resposta, 'E-mail ou senha incorretos.')
        self.assertNotIn('usuario_id', self.client.session)

    def test_email_nao_cadastrado(self):
        resposta = self.entrar('ninguem@teste.com')
        self.assertContains(resposta, 'E-mail ou senha incorretos.')
        self.assertNotIn('usuario_id', self.client.session)

    def test_formulario_vazio_nao_gera_erro(self):
        resposta = self.client.post(self.url, {})
        self.assertContains(resposta, 'E-mail ou senha incorretos.')

    def test_login_gera_uma_nova_sessao(self):
        self.client.get(self.url)
        sessao = self.client.session
        sessao['marcador'] = 'antes'
        sessao.save()
        chave_antes = sessao.session_key

        self.entrar('thiago@teste.com')
        self.assertNotEqual(self.client.session.session_key, chave_antes)
        # os dados da sessão continuam, só a chave muda
        self.assertEqual(self.client.session['marcador'], 'antes')

    def test_login_guarda_a_conta_na_lista_de_contas_usadas(self):
        self.entrar('thiago@teste.com')
        self.assertEqual(self.client.session['contas_utilizadas'], [self.usuario.id])
        self.entrar('thiago@teste.com')
        self.assertEqual(self.client.session['contas_utilizadas'], [self.usuario.id])
