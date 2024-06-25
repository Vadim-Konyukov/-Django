from django.contrib import admin

from .mixins import SearchResultsCategory
from .models import *


@admin.register(SpecUnit)
class SpecUnitAdmin(SearchResultsCategory, admin.ModelAdmin):
    search_fields = 'name',


@admin.register(SpecCategoryName)
class SpecCategoryNameAdmin(SearchResultsCategory, admin.ModelAdmin):
    search_fields = 'name',


admin.site.register(Spec)
admin.site.register(SearchFilterType)
admin.site.register(SpecUnitValidation)

