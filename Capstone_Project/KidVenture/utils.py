from django.db.models import Avg, Sum, Count
from django.db.models.functions import Length
from django.templatetags.static import static
from .models import Badge, GameProgress

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
    MIN_PLAYS = 5

    if stats['plays'] and stats['plays'] >= MIN_PLAYS:
        # Speedster
        if stats['avg_time'] and stats['avg_time'] < 10:
            badge, created = Badge.objects.get_or_create(
                student=student,
                name="Speedster",
                defaults={"image_url": static("KidVenture/images/badges/speedster.png")}
            )
            if created:
                new_badges.append(badge)

        # Accuracy Master
        if stats['total_mistakes'] is not None and stats['total_mistakes'] < 5:
            badge, created = Badge.objects.get_or_create(
                student=student,
                name="Accuracy Master",
                defaults={"image_url": static("KidVenture/images/badges/accuracy_master.png")}
            )
            if created:
                new_badges.append(badge)

        # Mismatch Minor
        if stats['total_mismatches'] is not None and stats['total_mismatches'] < 3:
            badge, created = Badge.objects.get_or_create(
                student=student,
                name="Mismatch Minor",
                defaults={"image_url": static("KidVenture/images/badges/mismatch_minor.png")}
            )
            if created:
                new_badges.append(badge)

    return new_badges
