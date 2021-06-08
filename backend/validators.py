
def raise_exception(msg):
    raise Exception(msg)

def validate_attrs(trigger, steps):
    from backend.transaction import Account
    required_attrs = dir(Account)

    params_trigger = trigger.get('params')
    user_id = params_trigger.get('user_id')
    pin = params_trigger.get('pin')

    if not isinstance(user_id, str):
        message = 'user_id must be str'
        raise_exception(message)

    if len(user_id) == 0:
        message = 'user_id Are required'
        raise_exception(message)

    if  not isinstance(pin, int):
        message = 'pin must be int'
        raise_exception(message)

    transitions = trigger.get('transitions', [])

    if len(transitions) == 0:
        message = 'Transitions are required to activate the trigger'
        raise_exception(message)

    for transition in transitions:
        target = transition.get('target', None)
        if not transition.get('target') in required_attrs:
            message = f'Transition {target} not available as transaction method'
            raise_exception(message)

    for step in steps:
        action = step.get('action')

        if action == '1':
            step['action'] = 'validate_account'

        if action is not None and action != '1' and not action in required_attrs :
            message = f'Invalid action [{action}] not available as a transaction method'
            raise_exception(message)

    return None, None


def account_exists(user_id, pin, collection):
    return collection.find_one({'user_id': user_id, 'pin': pin})
