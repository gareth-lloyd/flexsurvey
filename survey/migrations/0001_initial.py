# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('survey_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Project'])

        # Adding model 'Survey'
        db.create_table('survey_survey', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Project'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Survey'])

        # Adding model 'DesiredFact'
        db.create_table('survey_desiredfact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=512, db_index=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('data_type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('minimum', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('maximum', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('survey', ['DesiredFact'])

        # Adding model 'FactOption'
        db.create_table('survey_factoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desired_fact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.DesiredFact'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal('survey', ['FactOption'])

        # Adding unique constraint on 'FactOption', fields ['desired_fact', 'code']
        db.create_unique('survey_factoption', ['desired_fact_id', 'code'])

        # Adding model 'DesiredFactGroup'
        db.create_table('survey_desiredfactgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('heading', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('weight', self.gf('django.db.models.fields.FloatField')(default=1)),
        ))
        db.send_create_signal('survey', ['DesiredFactGroup'])

        # Adding model 'SurveyDesiredFact'
        db.create_table('survey_surveydesiredfact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Survey'])),
            ('desired_fact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.DesiredFact'])),
            ('fact_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.DesiredFactGroup'])),
            ('weight', self.gf('django.db.models.fields.FloatField')(default=1)),
        ))
        db.send_create_signal('survey', ['SurveyDesiredFact'])

        # Adding unique constraint on 'SurveyDesiredFact', fields ['survey', 'desired_fact']
        db.create_unique('survey_surveydesiredfact', ['survey_id', 'desired_fact_id'])

        # Adding model 'Fact'
        db.create_table('survey_fact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.Survey'])),
            ('desired_fact', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['survey.DesiredFact'])),
            ('data', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_by', to=orm['auth.User'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='updated_by', to=orm['auth.User'])),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('survey', ['Fact'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'SurveyDesiredFact', fields ['survey', 'desired_fact']
        db.delete_unique('survey_surveydesiredfact', ['survey_id', 'desired_fact_id'])

        # Removing unique constraint on 'FactOption', fields ['desired_fact', 'code']
        db.delete_unique('survey_factoption', ['desired_fact_id', 'code'])

        # Deleting model 'Project'
        db.delete_table('survey_project')

        # Deleting model 'Survey'
        db.delete_table('survey_survey')

        # Deleting model 'DesiredFact'
        db.delete_table('survey_desiredfact')

        # Deleting model 'FactOption'
        db.delete_table('survey_factoption')

        # Deleting model 'DesiredFactGroup'
        db.delete_table('survey_desiredfactgroup')

        # Deleting model 'SurveyDesiredFact'
        db.delete_table('survey_surveydesiredfact')

        # Deleting model 'Fact'
        db.delete_table('survey_fact')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 23, 14, 17, 6, 674165, tzinfo=<UTC>)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 11, 23, 14, 17, 6, 674037, tzinfo=<UTC>)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'survey.desiredfact': {
            'Meta': {'object_name': 'DesiredFact'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '512', 'db_index': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'maximum': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'minimum': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'surveys': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['survey.Survey']", 'through': "orm['survey.SurveyDesiredFact']", 'symmetrical': 'False'})
        },
        'survey.desiredfactgroup': {
            'Meta': {'object_name': 'DesiredFactGroup'},
            'heading': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '1'})
        },
        'survey.fact': {
            'Meta': {'object_name': 'Fact'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_by'", 'to': "orm['auth.User']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'desired_fact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.DesiredFact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Survey']"}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updated_by'", 'to': "orm['auth.User']"}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'survey.factoption': {
            'Meta': {'unique_together': "(('desired_fact', 'code'),)", 'object_name': 'FactOption'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'desired_fact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.DesiredFact']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'survey.project': {
            'Meta': {'object_name': 'Project'},
            'created_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'survey.survey': {
            'Meta': {'object_name': 'Survey'},
            'created_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'desired_facts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['survey.DesiredFact']", 'through': "orm['survey.SurveyDesiredFact']", 'symmetrical': 'False'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Project']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'survey.surveydesiredfact': {
            'Meta': {'unique_together': "(('survey', 'desired_fact'),)", 'object_name': 'SurveyDesiredFact'},
            'desired_fact': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.DesiredFact']"}),
            'fact_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.DesiredFactGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.Survey']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '1'})
        }
    }

    complete_apps = ['survey']
