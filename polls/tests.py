import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

#Tests could (and should, if this was a production app) be run on the Choice and Vote classes as well, but these tests will suffice for an example.

def create_question(question_text, days, add_choices=True):
	#question_text: The text of the question to be created.
	#days: Publication date of the question, expressed as an offset (in days) to the current time. Positive offsets are in the future, and negative ones in the past.
	#add_choices: Add boilerplate choices to the question to avoid any possible problems with a no-choice question during testing
	
	time = timezone.now() + datetime.timedelta(days=days)
	q = Question.objects.create(question_text=question_text, pub_date=time)
	
	if add_choices:
		q.choice_set.create(choice_text='Choice 1')
		q.choice_set.create(choice_text='Choice 2')
	
	return q

class QuestionDetailViewTests(TestCase):
	def test_future_question(self):
		#Attempting to access the detail view for a future question should result in a 404 error.
		
		future_question = create_question(question_text="Future question?", days=30)
		response = self.client.get(reverse('polls:detail', args=(future_question.id,)))
		self.assertEqual(response.status_code, 404)
	
	def test_past_question(self):
		#Attempting to access the detail view for a past question should succeed.
		
		past_question = create_question(question_text="Past question?", days=-30)
		response = self.client.get(reverse('polls:detail', args=(past_question.id,)))
		self.assertContains(response, past_question.question_text)

class QuestionIndexViewTests(TestCase):
	def test_no_questions(self):
		#if no questions are available, the index should return a message saying so
		
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'No polls are available.')
		self.assertQuerysetEqual(response.context['question_list'], [])
	
	def test_past_question(self):
		#questions published in the past should appear on the index page
		
		create_question(question_text="Past question?", days=-30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['question_list'], ['<Question: Past question?>'])
	
	def test_future_question(self):
		#questions published in the future should not appear on the index page
		
		create_question(question_text="Future question?", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['question_list'], [])
		
	def test_past_question_and_future_question(self):
		#questions published in the past should appear on the index page; questions with future publish dates should not
		
		create_question(question_text="Past question?", days=-30)
		create_question(question_text="Future question?", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['question_list'], ['<Question: Past question?>'])
	
	def test_multiple_past_questions(self):
		#the index page should be able to display multiple questions published in the past
		
		create_question(question_text="Past question 1?", days=-30)
		create_question(question_text="Past question 2?", days=-15)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['question_list'], ['<Question: Past question 1?>', '<Question: Past question 2?>'])
	
	def test_question_without_choices(self):
		#Questions without choices should not be visible
		
		create_question(question_text="Question?", days=-30, add_choices=False)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['question_list'], [])
	
	def test_question_with_choices(self):
		#Questions with choices should be visible
		
		create_question(question_text="Question?", days=-30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(response.context['question_list'], ['<Question: Question?>'])

class QuestionModelTests(TestCase):
	def test_was_published_recently_with_future_question(self):
		#should return False for questions with a publish date in the future
		
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertIs(future_question.was_published_recently(), False)
	
	def test_was_published_recently_with_old_question(self):
		#should return False for questions with a publish date older than one day

		time = timezone.now() + datetime.timedelta(days=-30)
		old_question = Question(pub_date=time)
		self.assertIs(old_question.was_published_recently(), False)
	
	def test_was_published_recently_with_recent_question(self):
		#should return True for questions with a publish date within one day

		time = timezone.now() + datetime.timedelta(hours=-12)
		recent_question = Question(pub_date=time)
		self.assertIs(recent_question.was_published_recently(), True)
		

class QuestionResultsViewTests(TestCase):
	def test_future_question(self):
		#Attempting to access the results view for a future question should result in a 404 error.
		
		future_question = create_question(question_text="Future question?", days=30)
		response = self.client.get(reverse('polls:results', args=(future_question.id,)))
		self.assertEqual(response.status_code, 404)
	
	def test_past_question(self):
		#Attempting to access the results view for a past question should succeed.
		
		past_question = create_question(question_text="Past question?", days=-30)
		response = self.client.get(reverse('polls:results', args=(past_question.id,)))
		self.assertContains(response, past_question.question_text)