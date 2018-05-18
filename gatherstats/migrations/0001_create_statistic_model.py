# Generated by Django 2.0.5 on 2018-05-08 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.URLField(help_text='URL of endpoint which this stat was fetched from', max_length=1204)),
                ('key', models.CharField(help_text='Dot-separated JavaScript style key path', max_length=512)),
                ('numeric_value', models.FloatField(help_text='Value of numeric statistic')),
                ('fetched_at', models.DateTimeField(help_text='Date and time when this statistic was fetched')),
            ],
        ),
        migrations.AddIndex(
            model_name='statistic',
            index=models.Index(fields=['endpoint', 'key', 'fetched_at'], name='gatherstats_endpoin_ca0383_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='statistic',
            unique_together={('endpoint', 'key', 'fetched_at')},
        ),
    ]
