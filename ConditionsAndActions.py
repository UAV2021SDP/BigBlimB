
def condition(data):
  return True

def action(data):
  # do something with data
  pass

fsm.add_transition(state1, state2, event).add_condition(condition)
fsm.add_transition(state1, state2, event).add_action(action)