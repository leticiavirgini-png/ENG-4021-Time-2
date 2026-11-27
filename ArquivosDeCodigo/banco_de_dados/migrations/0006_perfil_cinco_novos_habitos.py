from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banco_de_dados', '0005_avaliacao_medmap'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='acima_peso',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='perfil',
            name='pouca_fruta',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='perfil',
            name='dorme_pouco',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='perfil',
            name='sol_sem_protetor',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='perfil',
            name='sem_dentista',
            field=models.BooleanField(default=False),
        ),
    ]
