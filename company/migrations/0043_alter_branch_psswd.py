# Generated by Django 3.2.8 on 2023-12-06 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0042_alter_branch_psswd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branch',
            name='psswd',
            field=models.CharField(default='rs3ylgojly', max_length=10),
        ),
    ]
