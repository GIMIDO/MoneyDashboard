from .models import *
from django.db.models import Q

def calc_amount(actions):
    total_amount = 0
    for action in actions:
        if action.action_type == "increase":
            total_amount = total_amount + action.money
        else:
            total_amount -= action.money
    return total_amount


def search_actions(q_from, q_to, q_category, q_user):
    if q_category:
        actions_all = Action.objects.filter(user=q_user, category=q_category)
    else:
        actions_all = Action.objects.filter(user=q_user)

    if q_from:
        if q_to:    
            actions = actions_all.filter(
                Q(date__gte=q_from,date__lte=q_to))
        else:
            actions = actions_all.filter(
                Q(date__gte=q_from))
    else:
        if q_to:
            actions = actions_all.filter(
                    Q(date__lte=q_to))
        else:
            actions = actions_all
    return actions
