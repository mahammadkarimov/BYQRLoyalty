from django.contrib import admin
from loyalty.models import Programs, LoyaltyCategories


class ProgramsAdmin(admin.ModelAdmin):
    list_display = ("iiko_id", "name")
    list_display_links = ("iiko_id", "name")
    list_filter = ("iiko_id", "name")


class LoyaltyCategoriesAdmin(admin.ModelAdmin):
    list_display = ("iiko_id", "name", "program", "is_active")
    list_display_links = ("iiko_id", "name", "program", "is_active")
    list_filter = ("iiko_id", "name", "program", "is_active")


admin.site.register(Programs, ProgramsAdmin)
admin.site.register(LoyaltyCategories, LoyaltyCategoriesAdmin)
