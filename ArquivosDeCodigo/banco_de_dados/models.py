from django.db import models


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=128)

    def __str__(self):
        return self.nome


class Perfil(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class HistoricoFamiliar(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE
    )
    parente = models.CharField(max_length=50)
    doenca = models.CharField(max_length=150)
    idade_diagnostico = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.parente} - {self.doenca}"


class Cuidado(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE
    )
    tipo = models.CharField(max_length=30)
    nome = models.CharField(max_length=150)
    data = models.DateField()
    concluido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome} - {self.data}"
