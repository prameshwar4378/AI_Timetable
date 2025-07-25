# Generated by Django 5.2.2 on 2025-06-15 04:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Backend', '0002_remove_subject_name1'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailylecturetiming',
            name='lecture_name',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='breakclassassignment',
            unique_together={('lecture_timing',)},
        ),
        migrations.AlterField(
            model_name='dailylecturetiming',
            name='lecture_number',
            field=models.CharField(max_length=5),
        ),
        migrations.RemoveField(
            model_name='breakclassassignment',
            name='classroom',
        ),
        migrations.AddField(
            model_name='breakclassassignment',
            name='classroom',
            field=models.ManyToManyField(to='Backend.classroom'),
        ),
    ]
