from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from datetime import date
from django.utils.dateparse import parse_date
from banco_de_dados.models import Usuario, Perfil, HistoricoFamiliar as HistoricoFamiliarModel, Cuidado

def home(request):
    '''
    View function for home page of site.
    Renders the home.html template.
    '''
    return render(request, 'home.html')

def PerfilSaude(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Login')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    perfil = Perfil.objects.filter(usuario=usuario).first()
    mensagem = ''
    erro = ''

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        data_nascimento = parse_date(
            request.POST.get('data_nascimento', '')
        )
        sexo = request.POST.get('sexo', '').strip()

        if not nome or not data_nascimento or not sexo:
            erro = 'Preencha todos os campos do perfil.'
        else:
            if perfil:
                perfil.nome = nome
                perfil.data_nascimento = data_nascimento
                perfil.sexo = sexo
                perfil.save()
            else:
                perfil = Perfil.objects.create(
                    usuario=usuario,
                    nome=nome,
                    data_nascimento=data_nascimento,
                    sexo=sexo
                )

            mensagem = 'Perfil salvo com sucesso.'

    return render(request, 'PerfilSaude.html', {
        'usuario': usuario,
        'perfil': perfil,
        'mensagem': mensagem,
        'erro': erro
    })

def ComoUsar(request):


    return render(request, 'ComoUsar.html')


def EsqueciSenha (request):


    return render(request, 'EsqueciSenha.html')

def ConsentimentoDados(request):
    return render(request, 'ConsentimentoDados.html')

def CriarConta(request):

    if request.method == 'POST':

        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '')
        confirmar_senha = request.POST.get('confirmar_senha', '')

        
        if senha != confirmar_senha:
            return render(request, 'CriarConta.html', {
                'erro': 'As senhas não coincidem.',
                'nome': nome,
                'email': email
            })

        
        if len(senha) < 6:
            return render(request, 'CriarConta.html', {
                'erro': 'A senha deve ter pelo menos 6 caracteres.',
                'nome': nome,
                'email': email
            })

        
        if Usuario.objects.filter(email=email).exists():
            return render(request, 'CriarConta.html', {
                'erro': 'Este e-mail já está cadastrado.',
                'nome': nome,
                'email': email
            })

        
        usuario = Usuario.objects.create(
            nome=nome,
            email=email,
            senha=make_password(senha)
        )
        request.session['usuario_id'] = usuario.id
        return redirect('InicioLogado')


    return render(request, 'CriarConta.html')

def Artigos (request):


    return render(request, 'Artigos.html')

def EdicaoUsuario(request, usuario_id):

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':

        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '')

        
        email_existente = Usuario.objects.filter(
            email=email
        ).exclude(id=usuario.id).exists()

        if email_existente:
            return render(request, 'EdicaoUsuario.html', {
                'usuario': usuario,
                'erro': 'Este e-mail já está sendo utilizado.'
            })

        if not nome or not email:
            return render(request, 'EdicaoUsuario.html', {
                'usuario': usuario,
                'erro': 'Nome e e-mail são obrigatórios.'
            })

        usuario.nome = nome
        usuario.email = email

        
        if senha:
            if len(senha) < 6:
                return render(request, 'EdicaoUsuario.html', {
                    'usuario': usuario,
                    'erro': 'A nova senha deve ter pelo menos 6 caracteres.'
                })

            usuario.senha = make_password(senha)

        usuario.save()

        return redirect('InicioLogado')

    return render(request, 'EdicaoUsuario.html', {
        'usuario': usuario
    })

def PreferenciasNotificacoes(request):
    return render(request, 'PreferenciasNotificacoes.html')

def RemocaoUsuario(request, usuario_id):

    usuario = get_object_or_404(Usuario, id=usuario_id)

    if request.method == 'POST':

        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha', '')
        confirmacao = request.POST.get('confirmacao')

        
        if email != usuario.email:
            return render(request, 'RemocaoUsuario.html', {
                'usuario': usuario,
                'erro': 'O e-mail informado não corresponde à conta.'
            })

        
        if not check_password(senha, usuario.senha):
            return render(request, 'RemocaoUsuario.html', {
                'usuario': usuario,
                'erro': 'Senha incorreta.'
            })

        
        if confirmacao != 'sim':
            return render(request, 'RemocaoUsuario.html', {
                'usuario': usuario,
                'erro': 'Você precisa confirmar a exclusão.'
            })

        
        usuario.delete()
        request.session.flush()
        return redirect('home')

    return render(request, 'RemocaoUsuario.html', {
        'usuario': usuario
    })

def Tela(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        usuario = Usuario.objects.filter(email=email).first()

        if usuario and check_password(senha, usuario.senha):
            request.session['usuario_id'] = usuario.id
            return redirect('InicioLogado')

        return render(request, 'Tela.html', {'erro': 'E-mail ou senha incorretos.'})

    return render(request, 'Tela.html')

def HistoricoFamiliar(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()

    if not perfil:
        return redirect('PerfilSaude')

    if request.method == 'POST':
        HistoricoFamiliarModel.objects.create(
            perfil=perfil,
            parente=request.POST.get('parente'),
            doenca=request.POST.get('doenca'),
            idade_diagnostico=request.POST.get('idade')
        )

    historicos = HistoricoFamiliarModel.objects.filter(perfil=perfil)

    return render(request, 'HistoricoFamiliar.html', {'historicos': historicos})

def CheckupInteligente(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()

    if not perfil:
        return redirect('PerfilSaude')

    idade = date.today().year - perfil.data_nascimento.year
    sexo = perfil.sexo

    fuma = request.GET.get('fuma')
    bebe = request.GET.get('bebe')
    sedentario = request.GET.get('sedentario')

    # doencas de parentes de primeiro grau
    historicos = HistoricoFamiliarModel.objects.filter(perfil=perfil)
    parentes_proximos = ['Pai', 'Mãe', 'Irmão', 'Irmã', 'Irmão ou irmã']
    doencas = []

    for historico in historicos:
        if historico.parente in parentes_proximos:
            doencas.append(historico.doenca)

    recomendacoes = []

    # pressao
    if 'Hipertensão' in doencas or 'Infarto ou AVC' in doencas:
        recomendacoes.append('Medir a pressão pelo menos uma vez por ano, com atenção, porque há hipertensão, infarto ou AVC na família.')
    elif idade >= 18:
        recomendacoes.append('Medir a pressão pelo menos uma vez por ano.')

    # diabetes
    if 'Diabetes tipo 2' in doencas:
        recomendacoes.append('Fazer exame de glicemia de jejum agora e repetir a cada 3 anos, porque há diabetes na família.')
    elif idade >= 35:
        recomendacoes.append('Fazer exame de glicemia de jejum a cada 3 anos.')

    # colesterol
    if 'Colesterol alto' in doencas or 'Infarto ou AVC' in doencas:
        recomendacoes.append('Fazer exame de colesterol agora, porque há colesterol alto, infarto ou AVC na família.')
    elif idade >= 20:
        recomendacoes.append('Fazer exame de colesterol a cada 5 anos.')

    # mama
    if sexo == 'Feminino':
        if 'Câncer de mama' in doencas and idade >= 35:
            recomendacoes.append('Fazer mamografia uma vez por ano, porque há câncer de mama na família.')
        elif idade >= 50 and idade <= 74:
            recomendacoes.append('Fazer mamografia a cada 2 anos.')
        elif idade >= 40 and idade < 50:
            recomendacoes.append('Conversar com o médico sobre fazer mamografia.')

    # intestino
    if 'Câncer de intestino' in doencas:
        idade_inicio = 40
        for historico in historicos:
            if historico.doenca == 'Câncer de intestino' and historico.idade_diagnostico:
                if historico.idade_diagnostico - 10 < idade_inicio:
                    idade_inicio = historico.idade_diagnostico - 10
        if idade >= idade_inicio:
            recomendacoes.append('Fazer colonoscopia a cada 5 anos, porque há câncer de intestino na família.')
        else:
            recomendacoes.append('Começar a fazer colonoscopia aos ' + str(idade_inicio) + ' anos.')
    elif idade >= 45 and idade <= 75:
        recomendacoes.append('Conversar com o médico sobre exame para câncer de intestino.')

    # prostata
    if sexo == 'Masculino':
        if 'Câncer de próstata' in doencas and idade >= 45:
            recomendacoes.append('Conversar com o urologista sobre o exame de PSA, porque há câncer de próstata na família.')
        elif idade >= 50:
            recomendacoes.append('Conversar com o urologista sobre o exame de PSA.')

    # osteoporose
    if sexo == 'Feminino':
        if 'Osteoporose' in doencas and idade >= 50:
            recomendacoes.append('Fazer densitometria óssea, porque há osteoporose na família.')
        elif idade >= 65:
            recomendacoes.append('Fazer densitometria óssea.')

    # habitos
    if fuma:
        recomendacoes.append('Procurar ajuda para parar de fumar. O SUS oferece tratamento gratuito.')
        if idade >= 50 and idade <= 80:
            recomendacoes.append('Conversar com o médico sobre tomografia do pulmão.')

    if bebe:
        recomendacoes.append('Diminuir o consumo de álcool.')

    if sedentario:
        recomendacoes.append('Fazer pelo menos 150 minutos de atividade física por semana.')

    return render(request, 'CheckupInteligente.html', {
        'perfil': perfil,
        'idade': idade,
        'recomendacoes': recomendacoes,
        'fuma': fuma,
        'bebe': bebe,
        'sedentario': sedentario
    })

def ListarUsuarios(request):

    usuarios = Usuario.objects.all()

    return render(request, 'ListarUsuarios.html', {'usuarios': usuarios})


def CalendarioCuidados(request):

    usuario_id = request.session.get('usuario_id')
    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()

    cuidados = Cuidado.objects.filter(perfil=perfil)
    tipos_validos = ('Consulta', 'Exame', 'Vacina')

    tipo = request.GET.get('tipo', '')
    if tipo not in tipos_validos:
        tipo = ''
    if tipo:
        cuidados = cuidados.filter(tipo=tipo)

    inicio = request.GET.get('inicio', '')
    fim = request.GET.get('fim', '')
    mensagem_erro = ''

    try:
        inicio_data = parse_date(inicio) if inicio else None
    except ValueError:
        inicio_data = None

    try:
        fim_data = parse_date(fim) if fim else None
    except ValueError:
        fim_data = None

    if inicio and inicio_data is None:
        mensagem_erro = 'A data inicial informada é inválida.'
        inicio = ''
    if fim and fim_data is None:
        mensagem_erro = 'A data final informada é inválida.'
        fim = ''

    if inicio_data and fim_data and inicio_data > fim_data:
        mensagem_erro = 'A data inicial deve ser anterior ou igual à data final.'
        cuidados = Cuidado.objects.none()
    else:
        if inicio_data:
            cuidados = cuidados.filter(data__gte=inicio_data)
        if fim_data:
            cuidados = cuidados.filter(data__lte=fim_data)

    ordem = request.GET.get('ordem', 'asc')
    if ordem not in ('asc', 'desc'):
        ordem = 'asc'
    cuidados = cuidados.order_by('-data' if ordem == 'desc' else 'data', 'id')

    contexto = {
        'cuidados': cuidados,
        'hoje': date.today(),
        'tipos_cuidado': tipos_validos,
        'tipo_selecionado': tipo,
        'inicio': inicio,
        'fim': fim,
        'ordem': ordem,
        'mensagem_erro': mensagem_erro,
        'total_cuidados': cuidados.count(),
    }
    return render(request, 'CalendarioCuidados.html', contexto)

def RelatorioPreventivo(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Login')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    perfil = Perfil.objects.filter(usuario=usuario).first()
    mensagem = ''
    erro = ''

    if request.method == 'POST':
        if not perfil:
            erro = 'Cadastre o perfil de saúde antes de alterar o relatório.'
        else:
            acao = request.POST.get('acao', '')

            if acao == 'editar_historico':
                historico = get_object_or_404(
                    HistoricoFamiliarModel,
                    id=request.POST.get('historico_id'),
                    perfil=perfil
                )
                parente = request.POST.get('parente', '').strip()
                doenca = request.POST.get('doenca', '').strip()
                idade_texto = request.POST.get('idade_diagnostico', '').strip()

                try:
                    idade = int(idade_texto) if idade_texto else None
                except ValueError:
                    idade = -1

                if not parente or not doenca:
                    erro = 'Informe o parentesco e a condição de saúde.'
                elif idade is not None and (idade < 0 or idade > 120):
                    erro = 'A idade no diagnóstico deve estar entre 0 e 120 anos.'
                else:
                    historico.parente = parente
                    historico.doenca = doenca
                    historico.idade_diagnostico = idade
                    historico.save()
                    mensagem = 'Histórico familiar atualizado com sucesso.'

            elif acao == 'adicionar_historico':
                parente = request.POST.get('parente', '').strip()
                doenca = request.POST.get('doenca', '').strip()
                idade_texto = request.POST.get('idade_diagnostico', '').strip()

                try:
                    idade = int(idade_texto) if idade_texto else None
                except ValueError:
                    idade = -1

                if not parente or not doenca:
                    erro = 'Informe o parentesco e a condição de saúde.'
                elif idade is not None and (idade < 0 or idade > 120):
                    erro = 'A idade no diagnóstico deve estar entre 0 e 120 anos.'
                else:
                    HistoricoFamiliarModel.objects.create(
                        perfil=perfil,
                        parente=parente,
                        doenca=doenca,
                        idade_diagnostico=idade
                    )
                    mensagem = 'Histórico familiar adicionado com sucesso.'

            elif acao == 'editar_cuidado':
                cuidado = get_object_or_404(
                    Cuidado,
                    id=request.POST.get('cuidado_id'),
                    perfil=perfil
                )
                tipo = request.POST.get('tipo', '').strip()
                nome = request.POST.get('nome', '').strip()
                data_cuidado = parse_date(request.POST.get('data', ''))
                tipos_validos = ('Consulta', 'Exame', 'Vacina')

                if tipo not in tipos_validos or not nome or not data_cuidado:
                    erro = 'Preencha corretamente o tipo, o cuidado e a data.'
                else:
                    cuidado.tipo = tipo
                    cuidado.nome = nome
                    cuidado.data = data_cuidado
                    cuidado.save()
                    mensagem = 'Cuidado atualizado com sucesso.'

            elif acao == 'adicionar_cuidado':
                tipo = request.POST.get('tipo', '').strip()
                nome = request.POST.get('nome', '').strip()
                data_cuidado = parse_date(request.POST.get('data', ''))
                tipos_validos = ('Consulta', 'Exame', 'Vacina')

                if tipo not in tipos_validos or not nome or not data_cuidado:
                    erro = 'Preencha corretamente o tipo, o cuidado e a data.'
                else:
                    Cuidado.objects.create(
                        perfil=perfil,
                        tipo=tipo,
                        nome=nome,
                        data=data_cuidado
                    )
                    mensagem = 'Cuidado adicionado com sucesso.'
            else:
                erro = 'Não foi possível identificar a alteração solicitada.'

    if perfil:
        historicos = HistoricoFamiliarModel.objects.filter(
            perfil=perfil
        ).order_by('parente', 'doenca')
        cuidados = Cuidado.objects.filter(
            perfil=perfil
        ).order_by('data')
    else:
        historicos = HistoricoFamiliarModel.objects.none()
        cuidados = Cuidado.objects.none()

    return render(request, 'RelatorioPreventivo.html', {
        'usuario': usuario,
        'perfil': perfil,
        'historicos': historicos,
        'cuidados': cuidados,
        'mensagem': mensagem,
        'erro': erro
    })

def Familiares(request):

    usuario_id = request.session.get('usuario_id')
    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()

    familiares = HistoricoFamiliarModel.objects.filter(perfil=perfil)

    return render(request, 'Familiares.html', {'familiares': familiares})


def CadastroCuidados(request):
    return render(request, 'CadastroCuidados.html')

def InicioLogado(request):
    usuario_id = request.session.get('usuario_id')
    usuario = get_object_or_404(Usuario, id=usuario_id)

    return render(request, 'InicioLogado.html', {
        'usuario': usuario
    })
