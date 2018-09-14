from django.contrib import admin

from . import models


class FacebookAccountAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'fb_user_id',
        'date_created',
    )
    search_fields = ('user__username', 'user__email', 'fb_user_id')
    raw_id_fields = ('user',)


admin.site.register(models.FacebookAccount, FacebookAccountAdmin)
