import datetime
import textwrap

from django.db import models
from django.utils import timezone

class Question(models.Model):
	question_text = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published')
	
	def __str__(self):
		return textwrap.shorten(self.question_text, width=30, placeholder="...")
	
	def was_published_recently(self):
		now = timezone.now()
		return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)
	correct = models.BooleanField(null=True, default=None)
	
	def __str__(self):
		return textwrap.shorten(self.choice_text, width=30, placeholder="...")

class Vote(models.Model):
	choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
	signature = models.CharField(max_length=50)
	datetime = models.DateTimeField()
	
	def __str__(self):
		return self.signature + ", " + str(self.datetime.date()) + ", " + str(self.choice.question) + ", " + str(self.choice)