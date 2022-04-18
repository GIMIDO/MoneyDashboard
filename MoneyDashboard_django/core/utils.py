def calc_amount(actions):
    total_amount = 0
    for action in actions:
        if action.action_type == "increase":
            total_amount = total_amount + action.money
        else:
            total_amount -= action.money
    return total_amount