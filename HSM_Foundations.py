# foundational code primarily found at https://towardsdatascience.com/how-i-implemented-hfsm-in-python-65899c1fb1d0

# in order to be an HSM, we need to be able to...
# - be able to add a child state machine to a state
# - start a child state machine when parent state is entered
# - stop a child state machine when the parent state is exited
# - propagate an event to the lower-level state machine(s)
class State(object):
    def __init__(self, name, child_sm=None):
        self._name = name
        self._entry_callbacks: List[Callable[[Any], None]] = []
        self._exit_callbacks: List[Callable[[Any], None]] = []
        self._child_state_machine: Optional[StateMachine] = child_sm
        self._parent_state_machine: Optional[StateMachine] = None

    def __eq__(self, other):
        if other.name == self._name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __call__(self, data: Any):
        pass

    def on_entry(self, callback: Callable[[Any], None]):
        self._entry_callbacks.append(callback)

    def on_exit(self, callback: Callable[[], None]):
        self._exit_callbacks.append(callback)

    def set_child_sm(self, child_sm):
        if not isinstance(child_sm, StateMachine):
            raise TypeError("child_sm must be the type of StateMachine")
        if self._parent_state_machine and self._parent_state_machine == \
                child_sm:
            raise ValueError("child_sm and parent_sm must be different")
        self._child_state_machine = child_sm

    def set_parent_sm(self, parent_sm):
        if not isinstance(parent_sm, StateMachine):
            raise TypeError("parent_sm must be the type of StateMachine")
        if self._child_state_machine and self._child_state_machine == \
                parent_sm:
            raise ValueError("child_sm and parent_sm must be different")
        self._parent_state_machine = parent_sm

    def start(self, data: Any):
        for callback in self._entry_callbacks:
            callback(data)
        if self._child_state_machine is not None:
            self._child_state_machine.start(data)

    def stop(self, data: Any):
        for callback in self._exit_callbacks:
            callback(data)
        if self._child_state_machine is not None:
            self._child_state_machine.stop(data)

    def has_child_sm(self) -> bool:
        return True if self._child_state_machine else False

    @property
    def name(self):
        return self._name

    @property
    def child_sm(self):
        return self._child_state_machine

    @property
    def parent_sm(self):
        return self._parent_state_machine

# events essentially only have a name to keep track of them
class Event(object):
    def __init__(self, name):
        self._name = name

    def __eq__(self, other):
        if other.name == self._name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def name(self):
        return self._name

# there are 3 types of transitions:
# - Normal Transition: a normal transition from one state to another
# - Self Transition: a transition from and to itself
# - Null Transition: only executes the action, no entry or exit, useful for a "do" action in a state

class Transition(object):
    def __init__(self, event: Event, src: State, dst: State):
        self._event = event
        self._source_state = src
        self._destination_state = dst
        self._condition: Optional[Callable[[Any], bool]] = None
        self._action: Optional[Callable[[Any], None]] = None

    def __call__(self, data: Any):
        raise NotImplementedError

    def add_condition(self, callback: Callable[[Any], bool]):
        self._condition = callback

    def add_action(self, callback: Callable[[Any], Any]):
        self._action = callback

    @property
    def event(self):
        return self._event

    @property
    def source_state(self):
        return self._source_state

    @property
    def destination_state(self):
        return self._destination_state

# we need a seperate call function for each of the three transitions

class NormalTransition(Transition):
    def __init__(self, source_state: State, destination_state: State,
                 event: Event):
        super().__init__(event, source_state, destination_state)
        self._from = source_state
        self._to = destination_state

    def __call__(self, data: Any):
        if not self._condition or self._condition(data):
            if self._action:
                self._action(data)
            self._from.stop(data)
            self._to.start(data)

class SelfTransition(Transition):
    def __init__(self, source_state: State, event: Event):
        super().__init__(event, source_state, source_state)
        self._state = source_state

    def __call__(self, data: Any):
        if not self._condition or self._condition(data):
            if self._action:
                self._action(data)
            self._state.stop(data)
            self._state.start(data)

# the null transition isnt really a transition - there is no exiting or entering
# it only executes an action, if there is one
class NullTransition(Transition):
    def __init__(self, source_state: State, event: Event):
        super().__init__(event, source_state, source_state)
        self._state = source_state

    def __call__(self, data: Any):
        if not self._condition or self._condition(data):
            if self._action:
                self._action(data)

# an FSM has a collection of states, events, and transitions, exit and initial states
# it also has a name so we can keep track and have multiple
class StateMachine(object):
    def __init__(self, name):
        self._name = name
        self._states: List[State] = []
        self._events: List[Event] = []
        self._transitions: List[Transition] = []
        self._initial_state: Optional[State] = None
        self._current_state: Optional[State] = None
        self._exit_callback: Optional[Callable[[ExitState, Any], None]] = None
        self._exit_state = ExitState()
        self.add_state(self._exit_state)
        self._exited = True

    def __eq__(self, other):
        if other.name == self._name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self._name

    def start(self, data: Any):
        if not self._initial_state:
            raise ValueError("initial state is not set")
        self._current_state = self._initial_state
        self._exited = False
        self._current_state.start(data)

    def stop(self, data: Any):
        if not self._initial_state:
            raise ValueError("initial state is not set")
        if self._current_state is None:
            raise ValueError("state machine has not been started")
        self._current_state.stop(data)
        self._current_state = self._exit_state
        self._exited = True

    def on_exit(self, callback):
        self._exit_callback = callback

    def is_running(self) -> bool:
        if self._current_state and self._current_state != self._exit_state:
            return True
        else:
            return False

    def add_state(self, state: State, initial_state: bool = False):
        if state in self._states:
            raise ValueError("attempting to add same state twice")
        self._states.append(state)
        state.set_parent_sm(self)
        if not self._initial_state and initial_state:
            self._initial_state = state

    def add_event(self, event: Event):
        self._events.append(event)

    def add_transition(self, src: State, dst: State, evt: Event) -> \
            Optional[Transition]:
        transition = None
        if src in self._states and dst in self._states and evt in self._events:
            transition = NormalTransition(src, dst, evt)
            self._transitions.append(transition)
        return transition

    def add_self_transition(self, state: State, evt: Event) -> \
            Optional[Transition]:
        transition = None
        if state in self._states and evt in self._events:
            transition = SelfTransition(state, evt)
            self._transitions.append(transition)
        return transition

    def add_null_transition(self, state: State, evt: Event) -> \
            Optional[Transition]:
        transition = None
        if state in self._states and evt in self._events:
            transition = NullTransition(state, evt)
            self._transitions.append(transition)
        return transition

    # trigger event checks whether a transition can occur or not, if it is an exit state, and whether an exit callback should be called
    def trigger_event(self, evt: Event, data: Any = None, propagate: bool = False):
        transition_valid = False
        if not self._initial_state:
            raise ValueError("initial state is not set")

        if self._current_state is None:
            raise ValueError("state machine has not been started")

        if propagate and self._current_state.has_child_sm():
            self._current_state.child_sm.trigger_event(evt, data, propagate)
        else:
            for transition in self._transitions:
                if transition.source_state == self._current_state and \
                        transition.event == evt:
                    self._current_state = transition.destination_state
                    transition(data)
                    if isinstance(self._current_state, ExitState) and \
                            self._exit_callback and not self._exited:
                        self._exited = True
                        self._exit_callback(self._current_state, data)
                    transition_valid = True
                    break

    @property
    def exit_state(self):
        return self._exit_state

    @property
    def current_state(self):
        return self._current_state

    @property
    def name(self):






