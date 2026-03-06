from django.shortcuts import render, get_object_or_404, redirect
from poll.models import Question, Choice, UserVote
from django.db.models import F
from django.urls import reverse
from django.http import HttpResponseRedirect
# Create your views here.

def detail(request, question_id):
    question = get_object_or_404( Question, pk = question_id )
    user_already_voted = UserVote.objects.filter( user = request.user, question = question ).exists()
    return render( request, 'poll/detail.html', {'question': question, 'user_already_voted': user_already_voted} )

def vote(request, question_id):
    question = get_object_or_404( Question, pk = question_id )
    try:
        selected_choice = question.choice_set.get( pk = request.POST.get("choice") )
    except( KeyError, Choice.DoesNotExist ):
        return render( request, 'poll/detail.html', {'question': question}, {'error_message': 'You did not select any choices.'})
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        UserVote.objects.create( user = request.user, question = question )
        return HttpResponseRedirect( reverse('result', args=(question.id,)) )
    

def result(request, question_id):
    question = get_object_or_404( Question, pk = question_id )
    return render(request, 'poll/result.html', {'question': question, })