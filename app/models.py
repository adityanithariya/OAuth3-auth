from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from hashlib import sha256
from threading import Thread

# Model
class Session(models.Model):
    session_id = models.CharField(primary_key=True, max_length=100)
    client_id = models.CharField(max_length=100)
    req_scopes = models.CharField(max_length=100)
    allowed_scope = models.CharField(max_length=100)
    uid = models.CharField(max_length=100)
    authentication_token = models.CharField(max_length=100)
    access_token = models.CharField(max_length=100)
    session_start = models.DateTimeField(default=now)

    def save(self, *args, **kwargs) -> None:
        if (self.uid == ""):
            self.authentication_token = sha256(
                (self.client_id + self.allowed_scope + self.uid + str(now().timestamp())).encode()).hexdigest()
            self.access_token = sha256(
                (self.authentication_token + str(now().timestamp())).encode()).hexdigest()
        return super().save(*args, **kwargs)

    @property
    def delete_session(self):
        time = self.session_start + timedelta(days=1)
        query = Session.objects.get(pk=self.pk)

        def run():
            while True:
                if time < now():
                    query.delete()
                    break

        Thread(target=run).start()

    @property
    def delete_incomplete_session(self):
        time = self.session_start + timedelta(hours=1)
        query = Session.objects.get(pk=self.pk)

        def run():
            while True:
                if (time < now() and self.uid == ""):
                    query.delete()
                    break

        Thread(target=run).start()
