# Generated by Django 3.2.8 on 2024-05-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0125_alter_branch_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='psswd',
            field=models.CharField(default='l2Tf5XIe3P', max_length=10),
        ),
    ]
