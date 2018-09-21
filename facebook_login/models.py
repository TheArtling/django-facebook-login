from django.conf import settings
from django.db import models


class FacebookAccount(models.Model):
    """

    :user: FK to the Django user that this Facebook account is tied to.
    :fb_user_id: The Facebook user-id.
    :date_created: Date when this instance was created.

    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fb_user_id = models.CharField(unique=True, max_length=1024)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}'
