# Generated by Django 3.2.8 on 2021-10-28 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='XFileType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='XFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=150, unique=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='xfiles', to='xfiles.xfiletype')),
            ],
        ),
        migrations.CreateModel(
            name='ExContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('xfile_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ex_contents', to='xfiles.xfiletype')),
            ],
        ),
        migrations.CreateModel(
            name='Detail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='xfiles.content')),
            ],
        ),
        migrations.AddField(
            model_name='content',
            name='xfile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='xfiles.xfile'),
        ),
    ]
