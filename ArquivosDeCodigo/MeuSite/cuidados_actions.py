import calendar
from datetime import date

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from banco_de_dados.models import Cuidado, Perfil


# telas para onde o usuário pode voltar depois de concluir ou desfazer um cuidado.
# Qualquer outro valor (por exemplo, o endereço de um site externo) é ignorado.
DESTINOS_PERMITIDOS = ('CalendarioCuidados', 'InicioLogado')


def destino_seguro(voltar):
    if voltar in DESTINOS_PERMITIDOS:
        return voltar
    return 'CalendarioCuidados'


def somar_meses(data, meses):
    total = data.year * 12 + (data.month - 1) + meses
    ano, indice_mes = divmod(total, 12)
    mes = indice_mes + 1
    dia = min(data.day, calendar.monthrange(ano, mes)[1])
    return date(ano, mes, dia)


@require_POST
def atualizar_cuidado(request, cuidado_id):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('Tela')

    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()
    if not perfil:
        return redirect('PerfilSaude')

    cuidado = get_object_or_404(Cuidado, pk=cuidado_id, perfil=perfil)
    acao = request.POST.get('acao')

    if acao == 'desfazer':
        cuidado.concluido = False
        cuidado.save(update_fields=['concluido'])
    elif acao == 'concluir' and not cuidado.concluido:
        meses = request.POST.get('meses', '0')
        if meses not in ('0', '1', '3', '6', '12'):
            return redirect('CalendarioCuidados')

        cuidado.concluido = True
        cuidado.save(update_fields=['concluido'])
        if meses != '0':
            Cuidado.objects.create(
                perfil=perfil,
                tipo=cuidado.tipo,
                nome=cuidado.nome,
                data=somar_meses(date.today(), int(meses))
            )
    
    elif acao == 'apagar':
        cuidado.delete()

    return redirect(destino_seguro(request.POST.get('voltar')))
