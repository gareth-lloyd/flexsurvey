from django.contrib import admin
from survey.models import (Project, Survey, DesiredFact, FactOption,
        DesiredFactGroup, SurveyDesiredFact, Fact)

class ProjectAdmin(admin.ModelAdmin):
    pass
admin.site.register(Project, ProjectAdmin)

class SurveyDesiredFactInline(admin.TabularInline):
    model = Survey.desired_facts.through

class SurveyAdmin(admin.ModelAdmin):
    inlines = [
         SurveyDesiredFactInline,
    ]
    save_as = True
admin.site.register(Survey, SurveyAdmin)

class FactOptionInline(admin.TabularInline):
    model = FactOption
class DesiredFactAdmin(admin.ModelAdmin):
    inlines = [
         FactOptionInline,
         SurveyDesiredFactInline,
    ]
    search_fields = ['label']
admin.site.register(DesiredFact, DesiredFactAdmin)

class FactOptionAdmin(admin.ModelAdmin):
    pass
admin.site.register(FactOption, FactOptionAdmin)

class DesiredFactGroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(DesiredFactGroup, DesiredFactGroupAdmin)

class SurveyDesiredFactAdmin(admin.ModelAdmin):
    pass
admin.site.register(SurveyDesiredFact, SurveyDesiredFactAdmin)

class FactAdmin(admin.ModelAdmin):
    search_fields = ["survey__name","data","desired_fact__label","created_by__username","created_by__first_name","created_by__last_name"]
admin.site.register(Fact, FactAdmin)

