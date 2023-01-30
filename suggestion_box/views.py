from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .models import Suggestion


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ["title", "text", "post_anonymous"]


@login_required
def inbox(request):
    form = None
    if request.POST:
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.creator = request.user
            suggestion.save()
            form = None
    context = {"form": form or SuggestionForm(), "suggestions": Suggestion.objects.filter(archived=False)}
    return render(request, "suggestion_box/inbox.html", context)


@login_required
def suggestion_delete(request, suggestion_uuid):
    suggestion = Suggestion.objects.get(uuid=suggestion_uuid)
    suggestion.archived = True
    suggestion.save()
    return HttpResponse("")


@login_required
def suggestion_upvote(request, suggestion_uuid):
    context = {"suggestion": Suggestion.up_vote(suggestion_uuid, request.user)}
    return render(request, "suggestion_box/suggestion_details.html", context)


@login_required
def suggestion_downvote(request, suggestion_uuid):
    context = {"suggestion": Suggestion.down_vote(suggestion_uuid, request.user)}
    return render(request, "suggestion_box/suggestion_details.html", context)
