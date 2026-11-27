from datetime import date

from django.test import TestCase
from django.urls import reverse

from banco_de_dados.models import Cuidado, Perfil, Usuario


class TestesRedirecionamentoCuidados(TestCase):
    def setUp(self):
        usuario = Usuario.objects.create(nome='Pessoa', email='redirecionamento@teste.com', senha='teste')
        perfil = Perfil.objects.create(usuario=usuario, nome='Pessoa',
                                       data_nascimento=date(1990, 1, 1), sexo='Feminino')
        self.cuidado = Cuidado.objects.create(perfil=perfil, tipo='Exame',
                                              nome='Hemograma', data=date(2026, 12, 10))
        sessao = self.client.session
        sessao['usuario_id'] = usuario.id
        sessao.save()
        self.url = reverse('AtualizarCuidado', args=[self.cuidado.id])

    def concluir(self, **extra):
        dados = {'acao': 'concluir', 'meses': '0'}
        dados.update(extra)
        return self.client.post(self.url, dados)

    def test_volta_para_o_inicio_quando_vem_do_inicio(self):
        resposta = self.concluir(voltar='InicioLogado')
        self.assertRedirects(resposta, reverse('InicioLogado'), fetch_redirect_response=False)

    def test_sem_voltar_vai_para_o_calendario(self):
        resposta = self.concluir()
        self.assertRedirects(resposta, reverse('CalendarioCuidados'), fetch_redirect_response=False)

    def test_nao_redireciona_para_site_externo(self):
        resposta = self.concluir(voltar='https://site-malicioso.com')
        self.assertRedirects(resposta, reverse('CalendarioCuidados'), fetch_redirect_response=False)
        # o cuidado é concluído normalmente; só o destino perigoso é ignorado
        self.cuidado.refresh_from_db()
        self.assertTrue(self.cuidado.concluido)

    def test_nao_redireciona_para_endereco_sem_protocolo(self):
        resposta = self.client.post(self.url, {'acao': 'desfazer', 'voltar': '//site-malicioso.com'})
        self.assertRedirects(resposta, reverse('CalendarioCuidados'), fetch_redirect_response=False)

    def test_nao_redireciona_para_outra_tela_qualquer(self):
        resposta = self.client.post(self.url, {'acao': 'desfazer', 'voltar': '/RemocaoUsuario/1/'})
        self.assertRedirects(resposta, reverse('CalendarioCuidados'), fetch_redirect_response=False)
