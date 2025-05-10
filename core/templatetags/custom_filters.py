from django import template
from core.constants import TASKS_BY_CATEGORY


register = template.Library()
    
@register.filter(name='get_task_display')
def get_task_display(task_code, category):
    """
    Given a task code and a category, return the human-readable label from TASKS_BY_CATEGORY.
    If no match is found, return the original task_code.
    """
    for code, label in TASKS_BY_CATEGORY.get(category, []):
        if code == task_code:
            return label
    return task_code