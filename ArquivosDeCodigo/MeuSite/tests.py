from django.test import TestCase
from django.urls import reverse
from banco_de_dados.models import Usuario


class TesteCadastro(TestCase):

    def test_pagina_cadastro_abre(self):
        resposta=self.client.get(reverse('CriarConta'))
        self.assertEqual(resposta.status_code, 200)

    def test_cadastro_usuario_valido(self):
        dados = {
            'nome': 'Usuario Teste',
            'email': 'teste@exemplo.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha123'
        }

        resposta = self.client.post(
            reverse('CriarConta'),
            dados
        )

        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(
            Usuario.objects.filter(email='teste@exemplo.com').exists()
        )

    def test_cadastro_senhas_diferentes(self):
        dados = {
            'nome': 'Usuário Teste',
            'email': 'teste2@exemplo.com',
            'senha': 'senha123',
            'confirmar_senha': 'senha456'
        }

        resposta = self.client.post(
            reverse('CriarConta'),
            dados
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertFalse(
            Usuario.objects.filter(email='teste2@exemplo.com').exists()
        )

    def test_cadastro_email_duplicado(self):
        Usuario.objects.create(
            nome='Primeiro Usuário',
            email='teste@exemplo.com',
            senha='senha123'
        )

        dados = {
            'nome': 'Segundo Usuário',
            'email': 'teste@exemplo.com',
            'senha': 'senha456',
            'confirmar_senha': 'senha456'
        }

        resposta = self.client.post(
            reverse('CriarConta'),
            dados
        )

        self.assertEqual(resposta.status_code, 200)

        self.assertEqual(
            Usuario.objects.filter(email='teste@exemplo.com').count(),
            1
        )