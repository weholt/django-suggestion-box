from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

User = get_user_model()


SUGGESTION_STATUS = (
    ("pending", "Pending"),
    ("wont-do", "Won't do"),
    ("approved", "Approved"),
    ("implemented", "Implemented"),
    ("under-consideration", "Under consideration"),
)


class SuggestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related("up_votes", "down_votes")


class Suggestion(models.Model):
    """
    ...
    """

    uuid = models.UUIDField(default=uuid4, editable=False)
    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="suggestions"
    )
    created = models.DateTimeField(auto_now_add=True, editable=False)
    title = models.CharField(
        max_length=200, help_text="Short description of suggestion"
    )
    text = models.TextField(
        null=True,
        blank=True,
        help_text="Explaination of why this is an improvement or great idea",
    )
    post_anonymous = models.BooleanField(
        default=False, help_text="Don't display your name in the list of suggestions"
    )
    status = models.CharField(
        max_length=50, choices=SUGGESTION_STATUS, default="pending"
    )
    up_votes = models.ManyToManyField(User, blank=True, related_name="up_votes")
    down_votes = models.ManyToManyField(User, blank=True, related_name="down_votes")
    vote_status = models.IntegerField(default=0)
    notes = models.TextField(null=True, blank=True)
    processed = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    archived = models.BooleanField(default=False)

    objects = SuggestionManager()

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created"]
        verbose_name = "Suggestion"
        verbose_name_plural = "Suggestions"

    @property
    def vote_balance(self):
        up_vote_count = self.up_votes.all().count()
        down_vote_count = self.down_votes.all().count()
        return f"{self.vote_status} (+{up_vote_count}/-{down_vote_count})"

    @classmethod
    def up_vote(cls, suggestion_uuid: str, user: User) -> "Suggestion":
        suggestion = Suggestion.objects.get(uuid=suggestion_uuid)
        if user not in suggestion.up_votes.all():
            suggestion.up_votes.add(user)
        if user in suggestion.down_votes.all():
            suggestion.down_votes.remove(user)
        suggestion.vote_status = (
            suggestion.up_votes.all().count() - suggestion.down_votes.all().count()
        )
        suggestion.save()
        return suggestion

    @classmethod
    def down_vote(cls, suggestion_uuid: str, user: User) -> "Suggestion":
        suggestion = Suggestion.objects.get(uuid=suggestion_uuid)
        if user in suggestion.up_votes.all():
            suggestion.up_votes.remove(user)
        if user not in suggestion.down_votes.all():
            suggestion.down_votes.add(user)
        suggestion.vote_status = (
            suggestion.up_votes.all().count() - suggestion.down_votes.all().count()
        )
        suggestion.save()
        return suggestion


@receiver(post_save, sender=Suggestion)
@receiver(post_delete, sender=Suggestion)
def clear_the_cache(**kwargs):
    cache.clear()
