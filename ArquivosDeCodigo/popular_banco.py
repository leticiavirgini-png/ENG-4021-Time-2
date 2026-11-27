import os
import django
import random

from datetime import date, timedelta
from django.contrib.auth.hashers import make_password
from django.db import transaction


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MeuSite.settings')
django.setup()


from banco_de_dados.models import Usuario, Perfil, HistoricoFamiliar, Cuidado


pessoas = [
    ("Ana Silva", "ana"),
    ("Bruno Costa", "bruno"),
    ("Carla Oliveira", "carla"),
    ("Daniel Santos", "daniel"),
    ("Eduarda Lima", "eduarda"),
    ("Fernando Souza", "fernando"),
    ("Gabriela Rocha", "gabriela"),
    ("Henrique Alves", "henrique"),
    ("Isabela Martins", "isabela"),
    ("João Pereira", "joao"),
]

parentes = [
    ("Mãe", "Hipertensão", 52),
    ("Pai", "Diabetes tipo 2", 58),
    ("Irmão ou irmã", "Colesterol alto", 40),
    ("Mãe", "Câncer de mama", 47),
    ("Pai", "Câncer de intestino", 55),
    ("Irmão ou irmã", "Doença renal crônica", 43),
    ("Avó materna", "Osteoporose", 68),
    ("Avô paterno", "Glaucoma", 66),
]

cuidados = [
    ("Consulta", "Consulta clínica"),
    ("Exame", "Hemograma completo"),
    ("Vacina", "Vacina contra gripe"),
    ("Exame", "Exame de glicemia"),
    ("Consulta", "Consulta cardiológica"),
    ("Exame", "Exame de colesterol"),
    ("Consulta", "Consulta nutricional"),
    ("Vacina", "Vacina contra tétano"),
]


def gerar_data_nascimento():
    inicio = date(1960, 1, 1)
    fim = date(2005, 12, 31)
    intervalo = (fim - inicio).days
    return inicio + timedelta(days=random.randint(0, intervalo))


def criar_historicos(perfil, registros):
    for parente, doenca, idade in registros:
        HistoricoFamiliar.objects.create(
            perfil=perfil,
            parente=parente,
            doenca=doenca,
            idade_diagnostico=idade
        )


def criar_cuidados(perfil, registros):
    for tipo, nome, dias in registros:
        Cuidado.objects.create(
            perfil=perfil,
            tipo=tipo,
            nome=nome,
            data=date.today() + timedelta(days=dias)
        )


@transaction.atomic
def popular_banco():
    random.seed(42)

    total_perfis = 0
    total_historicos = 0
    total_cuidados = 0

    for nome, identificador in pessoas:
        email = f"{identificador}@medmap.com"

        usuario, _ = Usuario.objects.get_or_create(
            email=email,
            defaults={
                "nome": nome,
                "senha": make_password("MedMapDemo123!")
            }
        )

        usuario.nome = nome
        usuario.senha = make_password("MedMapDemo123!")
        usuario.save()

        Perfil.objects.filter(usuario=usuario).delete()

        if identificador == "ana":
            perfil = Perfil.objects.create(
                usuario=usuario,
                nome=nome,
                data_nascimento=date(1969, 12, 27),
                sexo="Feminino",
                sedentario=True,
                pouca_fruta=True
            )

            historicos = [
                ("Mãe", "Câncer de mama", 47),
                ("Pai", "Hipertensão", 50),
                ("Irmão ou irmã", "Diabetes tipo 2", 45),
            ]

            cuidados_da_ana = [
                ("Consulta", "Consulta clínica", 5),
                ("Exame", "Exame de colesterol", 12),
                ("Vacina", "Vacina contra gripe", 20),
                ("Exame", "Hemograma completo", 35),
            ]

            criar_historicos(perfil, historicos)
            criar_cuidados(perfil, cuidados_da_ana)
            total_historicos += len(historicos)
            total_cuidados += len(cuidados_da_ana)
        else:
            perfil = Perfil.objects.create(
                usuario=usuario,
                nome=nome,
                data_nascimento=gerar_data_nascimento(),
                sexo=random.choice(["Masculino", "Feminino"]),
                fuma=random.choice([True, False]),
                bebe=random.choice([True, False]),
                sedentario=random.choice([True, False]),
                acima_peso=random.choice([True, False]),
                pouca_fruta=random.choice([True, False]),
                dorme_pouco=random.choice([True, False]),
                sol_sem_protetor=random.choice([True, False]),
                sem_dentista=random.choice([True, False])
            )

            historicos = random.sample(parentes, 2)
            criar_historicos(perfil, historicos)

            cuidados_escolhidos = []
            for tipo, nome_cuidado in random.sample(cuidados, 3):
                cuidados_escolhidos.append(
                    (tipo, nome_cuidado, random.randint(3, 60))
                )

            criar_cuidados(perfil, cuidados_escolhidos)
            total_historicos += len(historicos)
            total_cuidados += len(cuidados_escolhidos)

        total_perfis += 1

    print("\n===== POPULAÇÃO DO MEDMAP CONCLUÍDA =====")
    print(f"Perfis recriados: {total_perfis}")
    print(f"Históricos familiares criados: {total_historicos}")
    print(f"Cuidados criados: {total_cuidados}")
    print("\nDados de acesso para demonstração:")
    print("Usuário: ana@medmap.com")
    print("Senha: MedMapDemo123!")


if __name__ == "__main__":
    popular_banco()
