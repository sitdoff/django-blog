# Generated by Django 4.2 on 2023-05-02 05:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0005_alter_post_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="is_draft",
            field=models.BooleanField(default=True, verbose_name="Черновик"),
        ),
        migrations.AlterField(
            model_name="post",
            name="is_published",
            field=models.BooleanField(default=False, verbose_name="Опубликовать"),
        ),
    ]
