# Generated by Django 3.2.9 on 2021-11-08 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DateRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('done', models.BooleanField(default=False)),
                ('archive', models.BooleanField(default=False)),
                ('points', models.IntegerField(default=1)),
                ('many_dateranges', models.ManyToManyField(blank=True, to='agendjang.DateRange')),
                ('many_tags', models.ManyToManyField(blank=True, to='agendjang.Tag')),
            ],
        ),
        migrations.AddField(
            model_name='daterange',
            name='task_myset',
            field=models.ManyToManyField(blank=True, to='agendjang.Task'),
        ),
        migrations.CreateModel(
            name='ScheduledTask',
            fields=[
                ('task_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='agendjang.task')),
                ('many_tasks', models.ManyToManyField(blank=True, related_name='linked_tasks', to='agendjang.Task')),
            ],
            bases=('agendjang.task',),
        ),
    ]
