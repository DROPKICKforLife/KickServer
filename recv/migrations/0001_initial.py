# Generated by Django 2.0b1 on 2017-11-08 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorAccounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctorID', models.TextField(max_length=20, verbose_name='DOCTORID')),
                ('doctorPW', models.TextField(max_length=20, verbose_name='DOCTORPW')),
                ('phone', models.TextField(max_length=11, verbose_name='PHONE')),
                ('sex', models.CharField(max_length=1, verbose_name='SEX')),
            ],
        ),
        migrations.CreateModel(
            name='UploadDatas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.TextField(max_length=20, verbose_name='USERID')),
                ('treeURL', models.TextField(max_length=20, verbose_name='TREEURL')),
                ('houseURL', models.TextField(max_length=100, verbose_name='HOUSEURL')),
                ('lastEdit', models.DateTimeField(verbose_name='LASTEDIT')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userID', models.TextField(max_length=20, verbose_name='USERID')),
                ('userPW', models.TextField(max_length=20, verbose_name='USERPW')),
                ('phone', models.TextField(max_length=11, verbose_name='PHONE')),
                ('sex', models.CharField(max_length=1, verbose_name='SEX')),
            ],
        ),
    ]