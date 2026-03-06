from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
# Create your models here.

class Question( models.Model ):
    user = models.ForeignKey( User, on_delete = models.CASCADE )
    question_text = models.CharField( max_length = 255 )
    pub_date = models.DateTimeField()
    
    def __str__(self):
        return self.question_text
    
    def was_published_recently(self):
        was_published_recently = self.pub_date > timezone.now() - datetime.timedelta( days = 1 )
        return was_published_recently
    

class Choice( models.Model ):
    user = models.ForeignKey( User, on_delete = models.CASCADE )
    question = models.ForeignKey( Question, on_delete = models.CASCADE )
    choice_text = models.CharField( max_length = 200 )
    votes = models.IntegerField( default = 0 )
    
    def __str__(self):
        return self.choice_text
    
    def get_percentage_vote(self):
        total_votes = self.question.choice_set.aggregate(models.Sum('votes'))['votes__sum'] or 0
        if total_votes == 0:
            return 0
        percentage = (self.votes / total_votes) * 100
        return round(percentage)


class UserVote( models.Model ):
    user = models.ForeignKey( User, on_delete = models.CASCADE )
    question = models.ForeignKey( Question, on_delete = models.CASCADE )
    voted_at = models.DateTimeField( auto_now_add = True )
    
    class Meta:
        unique_together = ('user', 'question')
    
    def __str__(self):
        return f"{self.user.username} voted on {self.question.question_text}"
    
