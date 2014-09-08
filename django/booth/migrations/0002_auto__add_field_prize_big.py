# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Prize.big'
        db.add_column(u'booth_prize', 'big',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Prize.big'
        db.delete_column(u'booth_prize', 'big')


    models = {
        u'booth.prize': {
            'Meta': {'ordering': "['name']", 'object_name': 'Prize'},
            'big': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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