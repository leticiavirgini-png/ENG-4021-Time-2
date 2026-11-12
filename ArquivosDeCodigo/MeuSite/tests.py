from django.test import TestCase
from django.urls import reverse


class TesteCadastro(TestCase):

    def test_pagina_cadastro_abre(self):
        resposta=self.client.get(reverse('CriarConta'))
        self.assertEqual(resposta.status_code, 200)