from django.urls import path

from . import views

app_name = "suggestion-box"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("delete/<uuid:suggestion_uuid>", views.suggestion_delete, name="delete"),
    path("up-vote/<uuid:suggestion_uuid>", views.suggestion_upvote, name="up-vote"),
    path("down-vote/<uuid:suggestion_uuid>", views.suggestion_downvote, name="down-vote"),
]
