from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from .models import Choice, Question, Vote

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'question_list'
	
	def get_queryset(self):
		#Chaining filter() and exclude() like this is the only way I could find to show only questions that have choices attached to them.
		#Not even replacing exclude(choice__isnull=True) with filter(choice__isnull=False) works.
		return Question.objects.filter(pub_date__lte=timezone.now()).exclude(choice__isnull=True).order_by('pub_date')

class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'
	
	def get_queryset(self):
		return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'
	
	def get_queryset(self):
		return Question.objects.filter(pub_date__lte=timezone.now())

def report(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	total_votes = 0; correct_votes = 0; incorrect_votes = 0
	
	for choice in question.choice_set.all():
		total_votes += choice.vote_set.all().count()
		correct_votes += choice.vote_set.filter(choice__correct=True).count()
		incorrect_votes += choice.vote_set.filter(choice__correct=False).count()
	
	most_recent_vote = Vote.objects.filter(choice__question=question).latest('datetime')
	
	return render(request, 'polls/report.html', {
		'question': question,
		'total_votes': total_votes,
		'correct_votes': correct_votes,
		'incorrect_votes': incorrect_votes,
		'most_recent_vote': most_recent_vote,
	})

def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	
	try:
		#get selected choice
		selected_choice = question.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		#no selected choice; redisplay question voting form
		return render(request, 'polls/detail.html', {
			'question': question,
			'error_message': "You didn't select a choice.",
		})
	else:
		#save vote to database
		date = datetime.strptime(request.POST['dateField'], '%Y-%m-%d')
		current_time = timezone.now().timetz()
		v = Vote(choice=selected_choice, signature=request.POST['signField'], datetime=datetime.combine(date, current_time))
		v.save()
		
		#create pass/fail message
		if selected_choice.correct:
			messages.add_message(request, messages.SUCCESS, '"' + str(selected_choice) + '" is correct!')
		else:
			messages.add_message(request, messages.ERROR, '"' + str(selected_choice) + '" is not correct.')
		
		#return HttpResponseRedirect to prevent double-submitting
		return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
