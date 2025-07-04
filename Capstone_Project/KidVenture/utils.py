import random
from django.db.models import Avg, Sum, Count
from django.db.models.functions import Length
from django.templatetags.static import static
from .models import Badge, GameProgress

def generate_random_username():
    adjectives = ["Swift", "Brave", "Quiet", "Witty", "Fuzzy", "Bold"]
    animals = ["Fox", "Lion", "Koala", "Otter", "Panda", "Eagle"]

    adjective = random.choice(adjectives)
    animal = random.choice(animals)
    number = random.randint(100, 999)

    return f"{adjective}{animal}{number}"

def award_badges(student):
    stats = GameProgress.objects.filter(
        user=student.user, is_free_play=False
    ).aggregate(
        plays            = Count('id'),
        avg_time         = Avg('time_taken'),
        total_mistakes   = Sum('mistakes'),
        total_mismatches = Sum(Length('mismatched_letters')),
    )

    new_badges = []
    MIN_PLAYS = 3

    if stats['plays'] and stats['plays'] >= MIN_PLAYS:
        # Speedster
        if stats['avg_time'] and stats['avg_time'] < 10:
            badge, created = Badge.objects.get_or_create(
                student=student.user,
                name="Speedster",
                defaults={"image": static("KidVenture/images/badges/speedster.png")}
            )
            if created:
                new_badges.append(badge)

        # Accuracy Master
        if stats['total_mistakes'] is not None and stats['total_mistakes'] < 5:
            badge, created = Badge.objects.get_or_create(
                student=student.user,
                name="Accuracy Master",
                defaults={"image": static("KidVenture/images/badges/accuracy_master.png")}
            )
            if created:
                new_badges.append(badge)

        # Mismatch Minor
        if stats['total_mismatches'] is not None and stats['total_mismatches'] < 3:
            badge, created = Badge.objects.get_or_create(
                student=student.user,
                name="Mismatch Minor",
                defaults={"image": static("KidVenture/images/badges/mismatch_minor.png")}
            )
            if created:
                new_badges.append(badge)

    return new_badges