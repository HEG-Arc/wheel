# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Quiz'
        db.create_table(u'booth_quiz', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('terminal', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('score', self.gf('django.db.models.fields.IntegerField')(default=0, max_length=5)),
            ('prize', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booth.Prize'], null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'booth', ['Quiz'])

        # Adding model 'Prize'
        db.create_table(u'booth_prize', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('percentage', self.gf('django.db.models.fields.IntegerField')(max_length=2)),
            ('stock', self.gf('django.db.models.fields.IntegerField')(max_length=5)),
        ))
        db.send_create_signal(u'booth', ['Prize'])


    def backwards(self, orm):
        # Deleting model 'Quiz'
        db.delete_table(u'booth_quiz')

        # Deleting model 'Prize'
        db.delete_table(u'booth_prize')


    models = {
        u'booth.prize': {
            'Meta': {'ordering': "['name']", 'object_name': 'Prize'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'percentage': ('django.db.models.fields.IntegerField', [], {'max_length': '2'}),
            'stock': ('django.db.models.fields.IntegerField', [], {'max_length': '5'})
        },
        u'booth.quiz': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Quiz'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prize': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['booth.Prize']", 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'max_length': '5'}),
            'terminal': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['booth']