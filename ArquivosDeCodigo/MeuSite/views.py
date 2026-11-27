from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from datetime import date, timedelta
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
        fuma = request.POST.get('fuma') == 'sim'
        bebe = request.POST.get('bebe') == 'sim'
        sedentario = request.POST.get('sedentario') == 'sim'
        acima_peso = request.POST.get('acima_peso') == 'sim'
        pouca_fruta = request.POST.get('pouca_fruta') == 'sim'
        dorme_pouco = request.POST.get('dorme_pouco') == 'sim'
        sol_sem_protetor = request.POST.get('sol_sem_protetor') == 'sim'
        sem_dentista = request.POST.get('sem_dentista') == 'sim'

        if not nome or not data_nascimento or not sexo:
            erro = 'Preencha todos os campos do perfil.'
        else:
            if perfil:
                perfil.nome = nome
                perfil.data_nascimento = data_nascimento
                perfil.sexo = sexo
                perfil.fuma = fuma
                perfil.bebe = bebe
                perfil.sedentario = sedentario
                perfil.acima_peso = acima_peso
                perfil.pouca_fruta = pouca_fruta
                perfil.dorme_pouco = dorme_pouco
                perfil.sol_sem_protetor = sol_sem_protetor
                perfil.sem_dentista = sem_dentista
                perfil.save()
            else:
                perfil = Perfil.objects.create(
                    usuario=usuario,
                    nome=nome,
                    data_nascimento=data_nascimento,
                    sexo=sexo,
                    fuma=fuma,
                    bebe=bebe,
                    sedentario=sedentario,
                    acima_peso=acima_peso,
                    pouca_fruta=pouca_fruta,
                    dorme_pouco=dorme_pouco,
                    sol_sem_protetor=sol_sem_protetor,
                    sem_dentista=sem_dentista
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

def MinhaConta(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    usuario = get_object_or_404(Usuario, id=usuario_id)
    contas_utilizadas = Usuario.objects.filter(
        id__in=request.session.get('contas_utilizadas', [])
    )

    return render(request, 'MinhaConta.html', {
        'usuario': usuario,
        'contas_utilizadas': contas_utilizadas
    })


def ConsentimentoDados(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    return render(request, 'ConsentimentoDados.html', {
        'usuario': usuario
    })

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
        contas=request.session.get('contas_utilizadas',[])
        if usuario.id not in contas:
            contas.append(usuario.id)
        request.session['contas_utilizadas']=contas
        request.session['usuario_id'] = usuario.id
        return redirect('InicioLogado')


    return render(request, 'CriarConta.html')

def Artigos (request):


    return render(request, 'Artigos.html')


def EdicaoUsuario(request, usuario_id):

    usuario_logado_id = request.session.get('usuario_id')

    if not usuario_logado_id:
        return redirect('Tela')

    if usuario_id != usuario_logado_id:
        return redirect('InicioLogado')

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
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    return render(request, 'PreferenciasNotificacoes.html', {
        'usuario': usuario
    })


def RemocaoUsuario(request, usuario_id):

    usuario_logado_id = request.session.get('usuario_id')

    if not usuario_logado_id:
        return redirect('Tela')

    if usuario_id != usuario_logado_id:
        return redirect('InicioLogado')

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
            contas=request.session.get('contas_utilizadas',[])

            if usuario.id not in contas:
                contas.append(usuario.id)

            request.session['contas_utilizadas']=contas
            request.session['usuario_id'] = usuario.id
            return redirect('InicioLogado')

        return render(request, 'Tela.html', {'erro': 'E-mail ou senha incorretos.'})

    return render(request, 'Tela.html')

def HistoricoFamiliar(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    perfil = Perfil.objects.filter(
        usuario_id=usuario_id
    ).first()

    if not perfil:
        return redirect('PerfilSaude')

    mensagem = ''
    erro = ''

    if request.method == 'POST':
        acao = request.POST.get('acao', 'adicionar')

        if acao == 'adicionar':
            parente = request.POST.get('parente', '').strip()
            doenca = request.POST.get('doenca', '').strip()
            idade_texto = request.POST.get('idade', '').strip()

            try:
                idade = int(idade_texto) if idade_texto else None
            except ValueError:
                idade = -1

            if not parente or not doenca:
                erro = 'Preencha o parentesco e a doença.'

            elif idade is not None and not 0 <= idade <= 120:
                erro = 'Informe uma idade entre 0 e 120 anos.'

            else:
                HistoricoFamiliarModel.objects.create(
                    perfil=perfil,
                    parente=parente,
                    doenca=doenca,
                    idade_diagnostico=idade
                )

                mensagem = 'Informação adicionada com sucesso.'

        elif acao == 'excluir':
            historico = get_object_or_404(
                HistoricoFamiliarModel,
                id=request.POST.get('historico_id'),
                perfil=perfil
            )

            historico.delete()
            mensagem = 'Registro removido com sucesso.'

    historicos = HistoricoFamiliarModel.objects.filter(
        perfil=perfil
    ).order_by('parente', 'doenca')

    return render(request, 'HistoricoFamiliar.html', {
        'historicos': historicos,
        'mensagem': mensagem,
        'erro': erro
    })

def CheckupInteligente(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()

    if not perfil:
        return redirect('PerfilSaude')

    if request.method == 'POST':
        nome = request.POST.get('nome')
        tipo = request.POST.get('tipo')

        ja_existe = Cuidado.objects.filter(
            perfil=perfil,
            nome=nome,
            concluido=False
        ).exists()

        if not ja_existe:
            Cuidado.objects.create(
                perfil=perfil,
                tipo=tipo,
                nome=nome,
                data=date.today() + timedelta(days=30)
            )

        return redirect('InicioLogado')

    idade = date.today().year - perfil.data_nascimento.year
    sexo = perfil.sexo

    fuma = perfil.fuma
    bebe = perfil.bebe
    sedentario = perfil.sedentario
    acima_peso = perfil.acima_peso
    pouca_fruta = perfil.pouca_fruta
    dorme_pouco = perfil.dorme_pouco
    sol_sem_protetor = perfil.sol_sem_protetor
    sem_dentista = perfil.sem_dentista

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
        recomendacoes.append({
            'texto': 'Medir a pressão pelo menos uma vez por ano, com atenção, porque há hipertensão, infarto ou AVC na família.',
            'nome': 'Medir a pressão',
            'tipo': 'Exame'
        })
    elif idade >= 18:
        recomendacoes.append({
            'texto': 'Medir a pressão pelo menos uma vez por ano.',
            'nome': 'Medir a pressão',
            'tipo': 'Exame'
        })

    # diabetes
    if 'Diabetes tipo 2' in doencas or (acima_peso and sedentario):
        if 'Diabetes tipo 2' in doencas:
            texto_diabetes = 'Fazer exame de glicemia de jejum agora e repetir a cada 3 anos, porque há diabetes na família.'
        else:
            texto_diabetes = 'Fazer exame de glicemia de jejum agora e repetir a cada 3 anos.'
        recomendacoes.append({
            'texto': texto_diabetes,
            'nome': 'Glicemia de jejum',
            'tipo': 'Exame'
        })
    elif idade >= 35:
        recomendacoes.append({
            'texto': 'Fazer exame de glicemia de jejum a cada 3 anos.',
            'nome': 'Glicemia de jejum',
            'tipo': 'Exame'
        })

    # colesterol
    if 'Colesterol alto' in doencas or 'Infarto ou AVC' in doencas:
        recomendacoes.append({
            'texto': 'Fazer exame de colesterol agora, porque há colesterol alto, infarto ou AVC na família.',
            'nome': 'Exame de colesterol',
            'tipo': 'Exame'
        })
    elif idade >= 20:
        recomendacoes.append({
            'texto': 'Fazer exame de colesterol a cada 5 anos.',
            'nome': 'Exame de colesterol',
            'tipo': 'Exame'
        })

    # mama
    if sexo == 'Feminino':
        if 'Câncer de mama' in doencas and idade >= 35:
            recomendacoes.append({
                'texto': 'Fazer mamografia uma vez por ano, porque há câncer de mama na família.',
                'nome': 'Mamografia',
                'tipo': 'Exame'
            })
        elif idade >= 50 and idade <= 74:
            recomendacoes.append({
                'texto': 'Fazer mamografia a cada 2 anos.',
                'nome': 'Mamografia',
                'tipo': 'Exame'
            })
        elif idade >= 40 and idade < 50:
            recomendacoes.append({
                'texto': 'Conversar com o médico sobre fazer mamografia.',
                'nome': 'Consulta sobre mamografia',
                'tipo': 'Consulta'
            })

    # intestino
    if 'Câncer de intestino' in doencas:
        idade_inicio = 40
        for historico in historicos:
            if historico.doenca == 'Câncer de intestino' and historico.idade_diagnostico:
                if historico.idade_diagnostico - 10 < idade_inicio:
                    idade_inicio = historico.idade_diagnostico - 10
        if idade >= idade_inicio:
            recomendacoes.append({
                'texto': 'Fazer colonoscopia a cada 5 anos, porque há câncer de intestino na família.',
                'nome': 'Colonoscopia',
                'tipo': 'Exame'
            })
        else:
            recomendacoes.append({
                'texto': 'Começar a fazer colonoscopia aos ' + str(idade_inicio) + ' anos.',
                'nome': '',
                'tipo': ''
            })
    elif idade >= 45 and idade <= 75:
        recomendacoes.append({
            'texto': 'Conversar com o médico sobre exame para câncer de intestino.',
            'nome': 'Consulta sobre câncer de intestino',
            'tipo': 'Consulta'
        })

    # prostata
    if sexo == 'Masculino':
        if 'Câncer de próstata' in doencas and idade >= 45:
            recomendacoes.append({
                'texto': 'Conversar com o urologista sobre o exame de PSA, porque há câncer de próstata na família.',
                'nome': 'Consulta com urologista (PSA)',
                'tipo': 'Consulta'
            })
        elif idade >= 50:
            recomendacoes.append({
                'texto': 'Conversar com o urologista sobre o exame de PSA.',
                'nome': 'Consulta com urologista (PSA)',
                'tipo': 'Consulta'
            })

    # osteoporose
    if sexo == 'Feminino':
        if 'Osteoporose' in doencas and idade >= 50:
            recomendacoes.append({
                'texto': 'Fazer densitometria óssea, porque há osteoporose na família.',
                'nome': 'Densitometria óssea',
                'tipo': 'Exame'
            })
        elif idade >= 65:
            recomendacoes.append({
                'texto': 'Fazer densitometria óssea.',
                'nome': 'Densitometria óssea',
                'tipo': 'Exame'
            })


    # pele
    if 'Câncer de pele (melanoma)' in doencas:
        recomendacoes.append({
            'texto': 'Consultar um dermatologista uma vez por ano para examinar a pele, porque há melanoma na família.',
            'nome': 'Consulta com dermatologista',
            'tipo': 'Consulta'
        })

    # glaucoma
    if 'Glaucoma' in doencas and idade >= 40:
        recomendacoes.append({
            'texto': 'Fazer exame de olhos com medida da pressão ocular a cada 1 a 2 anos, porque há glaucoma na família.',
            'nome': 'Exame de glaucoma',
            'tipo': 'Exame'
        })

    # ovario
    if 'Câncer de ovário' in doencas:
        recomendacoes.append({
            'texto': 'Conversar com o médico sobre aconselhamento genético, porque câncer de ovário na família pode indicar risco hereditário.',
            'nome': 'Consulta sobre aconselhamento genético',
            'tipo': 'Consulta'
        })

    # rins
    if 'Doença renal crônica' in doencas:
        recomendacoes.append({
            'texto': 'Fazer exame de creatinina no sangue e exame de urina uma vez por ano, porque há doença renal crônica na família.',
            'nome': 'Exame dos rins',
            'tipo': 'Exame'
        })

    # habitos
    if fuma:
        recomendacoes.append({
            'texto': 'Procurar ajuda para parar de fumar. O SUS oferece tratamento gratuito.',
            'nome': '',
            'tipo': ''
        })
        if idade >= 50 and idade <= 80:
            recomendacoes.append({
                'texto': 'Conversar com o médico sobre tomografia do pulmão.',
                'nome': 'Consulta sobre tomografia do pulmão',
                'tipo': 'Consulta'
            })

    if bebe:
        recomendacoes.append({
            'texto': 'Diminuir o consumo de álcool.',
            'nome': '',
            'tipo': ''
        })

    if sedentario:
        recomendacoes.append({
            'texto': 'Fazer pelo menos 150 minutos de atividade física por semana.',
            'nome': '',
            'tipo': ''
        })

    if acima_peso:
        recomendacoes.append({
            'texto': 'Procurar uma Unidade Básica de Saúde para avaliar o peso e receber orientação sobre alimentação e atividade física.',
            'nome': '',
            'tipo': ''
        })

    if pouca_fruta:
        recomendacoes.append({
            'texto': 'Comer frutas, verduras e legumes todos os dias e preferir alimentos naturais aos ultraprocessados.',
            'nome': '',
            'tipo': ''
        })

    if dorme_pouco:
        recomendacoes.append({
            'texto': 'Tentar dormir de 7 a 9 horas por noite e procurar um médico se o sono ruim continuar.',
            'nome': '',
            'tipo': ''
        })

    if sol_sem_protetor:
        recomendacoes.append({
            'texto': 'Usar protetor solar com FPS 30 ou mais e evitar o sol entre 10h e 16h.',
            'nome': '',
            'tipo': ''
        })
        recomendacoes.append({
            'texto': 'Observar a pele e procurar um dermatologista se notar pintas que mudam de cor, tamanho ou forma.',
            'nome': '',
            'tipo': ''
        })

    if sem_dentista:
        recomendacoes.append({
            'texto': 'Ir ao dentista pelo menos uma vez por ano.',
            'nome': 'Consulta com dentista',
            'tipo': 'Consulta'
        })

    nomes_no_calendario = []
    for cuidado in Cuidado.objects.filter(perfil=perfil, concluido=False):
        nomes_no_calendario.append(cuidado.nome)

    return render(request, 'CheckupInteligente.html', {
        'perfil': perfil,
        'idade': idade,
        'recomendacoes': recomendacoes,
        'nomes_no_calendario': nomes_no_calendario,
        'fuma': fuma,
        'bebe': bebe,
        'sedentario': sedentario,
        'acima_peso': acima_peso,
        'pouca_fruta': pouca_fruta,
        'dorme_pouco': dorme_pouco,
        'sol_sem_protetor': sol_sem_protetor,
        'sem_dentista': sem_dentista
    })

def ListarUsuarios(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    usuarios = Usuario.objects.filter(id=usuario_id)

    return render(request, 'ListarUsuarios.html', {
        'usuarios': usuarios
    })


def CadastroCuidados(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    perfil = Perfil.objects.filter(
        usuario_id=usuario_id
    ).first()

    if not perfil:
        return redirect('PerfilSaude')

    mensagem = ''
    erro = ''

    if request.method == 'POST':
        tipo = request.POST.get('tipo', '').strip()
        nome = request.POST.get('nome', '').strip()
        local = request.POST.get('local', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()
        data_cuidado = parse_date(
            request.POST.get('data', '')
        )

        tipos_validos = ('Consulta', 'Exame', 'Vacina')

        if tipo not in tipos_validos:
            erro = 'Selecione um tipo de cuidado válido.'

        elif not nome:
            erro = 'Informe o nome do cuidado.'

        elif not data_cuidado:
            erro = 'Informe uma data válida.'

        elif len(local) > 120 or len(observacoes) > 400:
            erro = 'Local ou observações ultrapassam o limite permitido.'

        else:
            Cuidado.objects.create(
                perfil=perfil,
                tipo=tipo,
                nome=nome,
                data=data_cuidado,
                local=local,
                observacoes=observacoes
            )

            return redirect('InicioLogado')

    return render(request, 'CadastroCuidados.html', {
        'mensagem': mensagem,
        'erro': erro
    })

def Familiares(request):

    usuario_id = request.session.get('usuario_id')
    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()

    familiares = HistoricoFamiliarModel.objects.filter(perfil=perfil)

    return render(request, 'Familiares.html', {'familiares': familiares})


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


def InicioLogado(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('Tela')
    usuario = get_object_or_404(Usuario, id=usuario_id)
    contas_ids=request.session.get('contas_utilizadas',[])
    contas_utilizadas=Usuario.objects.filter(
        id__in=contas_ids
    )

    perfil = Perfil.objects.filter(usuario_id=usuario_id).first()
    proximos_cuidados = Cuidado.objects.filter(
        perfil=perfil,
        concluido=False,
        data__gte=date.today()
    ).order_by('data')

    return render(request, 'InicioLogado.html', {
        'usuario': usuario,
        'contas_utilizadas': contas_utilizadas,
        'proximos_cuidados': proximos_cuidados
    })

def TrocarConta(request):
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('Tela')

    if request.method != 'POST':
        return redirect('InicioLogado')

    conta_id = request.POST.get('conta_id')
    senha = request.POST.get('senha', '')

    contas_ids = request.session.get('contas_utilizadas', [])

    try:
        conta_id = int(conta_id)
    except (TypeError, ValueError):
        return redirect('InicioLogado')

    if conta_id not in contas_ids:
        return redirect('InicioLogado')

    conta = Usuario.objects.filter(id=conta_id).first()

    if not conta or not check_password(senha, conta.senha):
        return render(request, 'MinhaConta.html', {
            'usuario': get_object_or_404(Usuario, id=usuario_id),
            'contas_utilizadas': Usuario.objects.filter(id__in=contas_ids),
            'erro_troca': 'Senha incorreta'
        })

    request.session.cycle_key()
    request.session['usuario_id'] = conta.id

    return redirect('InicioLogado')

def Sair(request):
    contas = request.session.get('contas_utilizadas', [])

    request.session.flush()

    request.session['contas_utilizadas'] = contas

    return redirect('home')
