from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banco_de_dados', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cuidado',
            name='concluido',
            field=models.BooleanField(default=False),
        ),
    ]
