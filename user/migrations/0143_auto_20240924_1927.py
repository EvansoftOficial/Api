# Generated by Django 3.2.8 on 2024-09-24 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0142_alter_employee_psswd'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='img',
            field=models.ImageField(blank=True, default='Img_User/withOut.png', null=True, upload_to='Img_User'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='psswd',
            field=models.CharField(default='yDqsXG2VHDlSQJcAnZi6', max_length=20, unique=True),
        ),
    ]
