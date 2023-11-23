# Generated by Django 4.2.7 on 2023-11-23 08:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Authors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('middle_name', models.CharField(max_length=100, verbose_name='Фамилия')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=100, verbose_name='Отчество')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('status', models.CharField(choices=[('Enabled', 'Действует'), ('Deleted', 'Удален')], default='Enabled', max_length=100, verbose_name='Статус')),
                ('country', models.CharField(blank=True, max_length=100, null=True, verbose_name='Страна')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='Город')),
                ('affiliation', models.CharField(blank=True, max_length=255, null=True, verbose_name='Организация')),
                ('biography', models.TextField(blank=True, verbose_name='Биография')),
                ('image', models.ImageField(null=True, upload_to='authors', verbose_name='Фотография')),
                ('time_create', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата добавления')),
                ('last_modified', models.DateTimeField(auto_now=True, null=True, verbose_name='Последнее изменение')),
            ],
            options={
                'verbose_name': 'Автор',
                'verbose_name_plural': 'Авторы',
                'db_table': 'authors',
                'ordering': ['id'],
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Articles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Название')),
                ('annotation', models.CharField(max_length=255, verbose_name='Аннотация')),
                ('description', models.TextField(blank=True, verbose_name='Текст статьи')),
                ('status', models.CharField(choices=[('Registered', 'Зарегистрирован'), ('Moderating', 'Проверяется'), ('Approved', 'Принято'), ('Denied', 'Отказано'), ('Deleted', 'Удалено')], default='Registered', max_length=100, verbose_name='Статус')),
                ('creation_date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('approving_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата формирования')),
                ('publication_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')),
                ('authors', models.ManyToManyField(related_name='articles', to='conference.authors', verbose_name='Автор')),
                ('moderator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='moderator_articles_set', to='account.customuser')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.customuser', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Статья',
                'verbose_name_plural': 'Статьи',
                'db_table': 'articles',
                'ordering': ['id'],
                'managed': True,
            },
        ),
    ]
