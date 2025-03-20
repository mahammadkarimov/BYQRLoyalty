from django.core.management.base import BaseCommand
from base_user.models import MyUser
from feedback.models import Question

class Command(BaseCommand):
    help = "Create questions for specific users"

    def handle(self, *args, **kwargs):
        # Fetch the users with specific usernames
        shekipark_user = MyUser.objects.filter(username="shekipark-hotel").first()
        premiumpark_user = MyUser.objects.filter(username="premiumpark-hotel").first()
        questions = Question.objects.filter(user=shekipark_user)
        for q in questions:
            question = Question.objects.create(
                user=premiumpark_user,
<<<<<<< HEAD
                question=q.question
=======
                question=q
>>>>>>> 6a392f39d74ccf49121536f45e261fdbc8802179
            )
            question.save()
            self.stdout.write(self.style.SUCCESS("Question created for Premiumpark Hotel user."))
