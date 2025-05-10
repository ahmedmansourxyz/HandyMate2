from django import template
from core.models import Review
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter
def has_review(job):
    """
    Returns True if the job already has an associated review.
    """
    try:
        # Try to access the related review via the one-to-one field.
        job.review
        return True
    except Review.DoesNotExist:
        return False

@register.filter
def star_rating(value):
    """
    Given a numeric rating, returns HTML with full, half, and empty star icons.
    Assumes a 5-star scale.
    """
    try:
        rating = float(value)
    except (ValueError, TypeError):
        rating = 0.0

    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    html = (
        '<i class="fas fa-star text-warning"></i>' * full_stars +
        '<i class="fas fa-star-half-alt text-warning"></i>' * half_star +
        '<i class="far fa-star text-warning"></i>' * empty_stars
    )
    return mark_safe(html)