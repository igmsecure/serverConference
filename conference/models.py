# Create your models here.
from django.db import models
from django.urls import reverse
from account.models import CustomUser


class Authors(models.Model):

    STATUS_CHOICES = (
        ('Enabled', 'Действует'),
        ('Deleted', 'Удален'),
    )

    middle_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Отчество")
    date_of_birth = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Enabled', verbose_name="Статус")
    country = models.CharField(max_length=100, verbose_name="Страна", blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name="Город", blank=True, null=True)
    affiliation = models.CharField(max_length=255, verbose_name="Организация", blank=True, null=True)
    biography = models.TextField(verbose_name="Биография", blank=True)
    image = models.ImageField(null=True, upload_to="authors", verbose_name="Фотография")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления", null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Последнее изменение", null=True, blank=True)

    class Meta:
        db_table = 'authors'
        managed = True
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['id']

    def __str__(self): 
        return f"{self.first_name} {self.middle_name}"

    def get_absolute_url(self):
        return reverse('author', kwargs={'author_id':self.pk})
    


class Articles(models.Model):

    STATUS_CHOICES = [
        ('Registered', 'Зарегистрирован'),
        ('Moderating', 'Проверяется'),
        ('Approved', 'Принято'),
        ('Denied', 'Отказано'),
        ('Deleted', 'Удалено')
    ]

    title = models.CharField(max_length=100, verbose_name="Название")
    annotation = models.CharField(max_length=255, verbose_name="Аннотация")
    description = models.TextField(verbose_name="Текст статьи", blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Registered', verbose_name="Статус")
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE, verbose_name="Пользователь", blank=True, null=True)
    moderator = models.ForeignKey(CustomUser, models.DO_NOTHING, related_name='moderator_articles_set', blank=True, null=True)
    authors = models.ManyToManyField(Authors, verbose_name="Автор", related_name='articles')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", blank=True, null=True)
    approving_date = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    publication_date = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    def __str__(self): 
        return self.title

    class Meta:
        db_table = 'articles'
        managed = True
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['id']
