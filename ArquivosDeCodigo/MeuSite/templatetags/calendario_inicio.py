import calendar
from datetime import date, timedelta

from django import template
from banco_de_dados.models import Cuidado

register = template.Library()


@register.inclusion_tag('includes/CalendarioResumoInicio.html', takes_context=True)
def calendario_inicio(context):
    request = context['request']
    hoje = date.today()
    mes_pedido = request.GET.get('mes', '')
    try:
        if len(mes_pedido) == 7 and mes_pedido[4] == '-':
            ano, mes = map(int, mes_pedido.split('-'))
            if not 2000 <= ano <= 2099:
                raise ValueError
            primeiro_dia = date(ano, mes, 1)
        else:
            primeiro_dia = hoje.replace(day=1)
    except ValueError:
        primeiro_dia = hoje.replace(day=1)

    ano = primeiro_dia.year
    mes = primeiro_dia.month
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
    usuario_id = request.session.get('usuario_id')

    dias_com_cuidado = set()
    if usuario_id:
        dias_com_cuidado = set(
            Cuidado.objects.filter(
                perfil__usuario_id=usuario_id,
                data__range=(primeiro_dia, ultimo_dia)
            ).values_list('data', flat=True)
        )

    semanas = []
    for semana in calendar.Calendar(firstweekday=6).monthdatescalendar(ano, mes):
        dias = []
        for dia in semana:
            dias.append({
                'numero': dia.day,
                'dia_iso': dia.isoformat(),
                'no_mes': dia.month == mes,
                'com_cuidado': dia in dias_com_cuidado,
                'hoje': dia == hoje,
            })
        semanas.append(dias)

    mes_anterior = (primeiro_dia - timedelta(days=1)).strftime('%Y-%m')
    proximo_mes = (ultimo_dia + timedelta(days=1)).strftime('%Y-%m')

    nomes = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    return {
        'mes_nome': nomes[mes - 1],
        'ano': ano,
        'semanas': semanas,
        'mes_anterior': mes_anterior,
        'proximo_mes': proximo_mes,
    }
