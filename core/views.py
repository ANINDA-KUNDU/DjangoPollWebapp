from django.shortcuts import render
from poll.models import Question, Choice
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def home(request):
    latest_question_list = Question.objects.order_by( "-pub_date" )[:5]
    return render(request, 'core/home.html', {'latest_question_list': latest_question_list })