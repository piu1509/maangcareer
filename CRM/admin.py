from collections.abc import Sequence
from typing import Sequence
from django.contrib import admin
from django.http.request import HttpRequest
from .models import *
from userManagement.models import SalesPerson
from import_export.admin import ImportMixin
from django.utils import timezone


admin.site.register(socialMediaRefCode)

@admin.action(description='Selected contacts to be auto-assigned')
def make_published(modeladmin, request, queryset):
    if request.user.groups.filter(name='Sales Managers').exists() or request.user.is_superuser:
        sp = SalesPerson.objects.filter(user__is_active=True)
        if sp.count():
            for i,contact in enumerate(queryset):
                contact.assigned_sales_person = sp[i % sp.count()]
                if not contact.assigned_date:contact.assigned_date = timezone.now()
                contact.save()

class contactInfoAdmin(ImportMixin, admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Sales Managers').exists() or request.user.is_superuser:
            return qs
        return qs.filter(assigned_sales_person=request.user.salesperson)

    def get_list_display(self, request: HttpRequest) -> Sequence[str]:
        if request.user.groups.filter(name='Sales Managers').exists() or request.user.is_superuser:
            return (
                "name",
                "assigned_sales_person",
                "assigned_date",
                "follow_up_date",
                "status",
                "ref"
            )
        return (
            "name",
            "status",
            "assigned_date",
            "follow_up_date",
            "ref"
        )

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "status":
            kwargs["choices"] = [
                ('0','Not Contacted'),
                ('1','Not Answered'),
                ('2','Follow Up'),
                ('3','Not Interested'),
            ]
            if request.user.groups.filter(name='Sales Managers').exists() or request.user.is_superuser:
                kwargs["choices"].append(('4','Converted'))
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
    def get_readonly_fields(self, request, obj):
        if request.user.groups.filter(name='Sales Callers').exists():
            return (
                'name',
                'phone_number',
                'email',
                'location',
                'university',
                'ref',
                'assigned_sales_person',
            )
        return ()

    search_fields = (
        'name',
        'email',
        'phone_number'
    )

    # list_editable = ("assigned_sales_person",)

    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        if request.user.groups.filter(name='Sales Managers').exists() or request.user.is_superuser: return (
            "status",
            "ref",
            "follow_up_date",
            "assigned_date",
            "assigned_sales_person"
        )
        return (
            "status",
            "ref",
            "follow_up_date",
            "assigned_date",
        )

    actions = (
        make_published,
    )
admin.site.register(contactInfo, contactInfoAdmin)