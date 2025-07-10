import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from tasks.models import Category, Task

class Command(BaseCommand):
    help = "Seed database with initial categories, a user, and some tasks."

    def handle(self, *args, **options):
        # 1) Categories + colour codes
        categories = [
            ("Painkillers",       "#e4c1f9"),
            ("Physio Exercises",  "#fcf6bd"),
            ("Ice & Compression", "#d0f4de"),
            ("Milestones",        "#a9def9"),
        ]
        for name, colour in categories:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={"colour_code": colour}
            )
            if created:
                self.stdout.write(f"  • Created category {name} ({colour})")

        # 2) Test user
        User = get_user_model()
        email = "darcy@test.com"
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username="darcy",
                email=email,
                password="password"
            )
            self.stdout.write(f"  • Created user {email} / password='password'")
        else:
            user = User.objects.get(email=email)
            self.stdout.write(f"  • User {email} already exists")

        # 3) Example tasks
        raw_tasks = [
            {"title": "Remove bandage",       "category": "Milestones",       "note": None, "start": (2025,7,2,9,0)},
            {"title": None,                   "category": "Physio Exercises", "note": None, "start": (2025,7,2,8,0)},
            {"title": "ACL reconstruction surgery", "category": "Milestones","note": None, "start": (2025,6,30,12,0)},
            {"title": "co-dydramol",          "category": "Painkillers",     "note": None, "start": (2025,6,30,22,30)},
            {"title": "co-dydramol",          "category": "Painkillers",     "note": None, "start": (2025,7,1,3,0)},
            {"title": "Naproxen",             "category": "Painkillers",     "note": None, "start": (2025,7,1,10,28)},
        ]
        for data in raw_tasks:
            cat = Category.objects.get(name=data["category"])
            # build an aware datetime
            dt = datetime.datetime(*data["start"])
            aware_dt = timezone.make_aware(dt, timezone.get_current_timezone())
            task, created = Task.objects.get_or_create(
                title=data["title"],
                category=cat,
                user=user,  # associate with the test user
                defaults={
                    "notes": data["note"],
                    "start_time": aware_dt,
                    "done": False,
                }
            )
            if created:
                self.stdout.write(f"  • Created task {task!r}")

        self.stdout.write(self.style.SUCCESS("✅ Database seeding complete."))
