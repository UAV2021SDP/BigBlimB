"""
Hierarchical Finite State Machine
Description:
    HFSM (Hierarchical Finite State Machine) implements full feature of HFSM.
License:
    Copyright 2020 Debby Nirwan
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
# foundational code primarily found at https://towardsdatascience.com/how-i-implemented-hfsm-in-python-65899c1fb1d0
# github of code at https://github.com/debbynirwan/hfsm

#just used for ease of catching errors
import logging
from typing import List, Any, Optional, Callable
#used for test harness
from unittest.mock import MagicMock

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

class ExitState(State):

    def __init__(self, status="Normal"):
        self._name = "ExitState"
        self._status = status
        super().__init__(self._status + self._name)

    @property
    def status(self):
        return self._status

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
        return self._name


# ---------------Test Harness---------------#

class TestEvent:
    def test_event_constructor(self):
        event = Event("event")
        assert event.name == "event"

    def test_equality(self):
        event1 = Event("event")
        event2 = Event("event")
        assert event1 == event2

class TestState:
    def test_constructor_default(self):
        state = State("state")
        assert state.name == "state"
        assert state.child_sm is None
        assert not state.has_child_sm()

    def test_constructor_with_child(self):
        child_state_machine = StateMachine("state_machine")
        state = State("state", child_state_machine)
        assert state.name == "state"
        assert state.child_sm is not None
        assert state.has_child_sm()

    def test_equality(self):
        state1 = State("state")
        state2 = State("state")
        assert state1 == state2

    def test_set_child_sm(self):
        child_state_machine = StateMachine("state_machine")
        state = State("state")
        assert state.child_sm is None
        assert not state.has_child_sm()
        state.set_child_sm(child_state_machine)
        assert state.child_sm is not None
        assert state.has_child_sm()

    def test_set_parent_sm(self):
        parent_state_machine = StateMachine("state_machine")
        state = State("state")
        assert state.parent_sm is None
        state.set_parent_sm(parent_state_machine)
        assert state.parent_sm is not None

    def test_on_entry(self):
        callback = MagicMock()
        state = State("state")
        state.on_entry(callback)
        state.start("data")
        callback.assert_called_once_with("data")

    def test_on_exit(self):
        callback = MagicMock()
        state = State("state")
        state.on_exit(callback)
        state.start("data")
        state.stop("data")
        callback.assert_called_once_with("data")

class TestExitState:
    def test_exit_state_constructor_default(self):
        exit_state = ExitState()
        assert exit_state.name == "NormalExitState"
        assert exit_state.status == "Normal"

    def test_exit_state_constructor_with_status(self):
        exit_state = ExitState("Error")
        assert exit_state.name == "ErrorExitState"
        assert exit_state.status == "Error"

class TestStateMachine:
    def test_sm_constructor(self):
        state_machine = StateMachine("sm")
        exit_state = ExitState()
        assert state_machine.name == "sm"
        assert state_machine.current_state is None
        assert state_machine.exit_state == exit_state

    def test_equality(self):
        state_machine1 = StateMachine("sm")
        state_machine2 = StateMachine("sm")
        assert state_machine1 == state_machine2

    def test_with_initial_state(self):
        state_machine = StateMachine("sm")
        initial_state = State("initial_state")
        entry_cb = MagicMock()
        initial_state.on_entry(entry_cb)
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.start("data")
        assert state_machine.current_state == initial_state
        entry_cb.assert_called_once_with("data")
        assert state_machine.is_running()

    def test_transition_with_invalid_event(self):
        state_machine = StateMachine("sm")
        initial_state = State("initial_state")
        second_state = State("second_state")
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_state(second_state)
        assert state_machine.add_transition(initial_state,
                                            second_state, event) is None

    def test_transition_with_valid_event(self):
        state_machine = StateMachine("sm")
        initial_state = State("initial_state")
        second_state = State("second_state")
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_state(second_state)
        state_machine.add_event(event)
        assert state_machine.add_transition(initial_state,
                                            second_state, event) is not None

    def test_self_transition_with_invalid_event(self):
        state_machine = StateMachine("sm")
        initial_state = State("initial_state")
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        assert state_machine.add_self_transition(initial_state, event) is None

    def test_self_transition_with_valid_event(self):
        state_machine = StateMachine("sm")
        initial_state = State("initial_state")
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_event(event)
        assert state_machine.add_self_transition(initial_state,
                                                 event) is not None

    def test_null_transition_with_invalid_event(self):
        state_machine = StateMachine("sm")
        initial_state = State("initial_state")
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        assert state_machine.add_null_transition(initial_state,
                                                 event) is None

    def test_null_transition_with_valid_event(self):
        state_machine = StateMachine("sm")
        initial_state = State("initial_state")
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_event(event)
        assert state_machine.add_null_transition(initial_state,
                                                 event) is not None

    def test_event_trigger(self):
        state_machine = StateMachine("sm")
        exit_cb = MagicMock()
        entry_cb = MagicMock()
        initial_state = State("initial_state")
        second_state = State("second_state")
        initial_state.on_exit(exit_cb)
        second_state.on_entry(entry_cb)
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_state(second_state)
        state_machine.add_event(event)
        state_machine.add_transition(initial_state, second_state, event)
        state_machine.start("data")
        exit_cb.assert_not_called()
        entry_cb.assert_not_called()
        state_machine.trigger_event(event, "data")
        exit_cb.assert_called_once_with("data")
        entry_cb.assert_called_once_with("data")

    def test_event_trigger_propagate_but_no_child_sm(self):
        state_machine = StateMachine("sm")
        exit_cb = MagicMock()
        entry_cb = MagicMock()
        initial_state = State("initial_state")
        second_state = State("second_state")
        initial_state.on_exit(exit_cb)
        second_state.on_entry(entry_cb)
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_state(second_state)
        state_machine.add_event(event)
        state_machine.add_transition(initial_state, second_state, event)
        state_machine.start("data")
        exit_cb.assert_not_called()
        entry_cb.assert_not_called()
        state_machine.trigger_event(event, "data", propagate=True)
        # no child fsm in current state, so the event is caught in this fsm
        assert state_machine.current_state == second_state

    @staticmethod
    def create_child_fsm():
        state_machine = StateMachine("child_sm")
        exit_cb = MagicMock()
        entry_cb = MagicMock()
        initial_state = State("child_initial_state")
        second_state = State("child_second_state")
        initial_state.on_exit(exit_cb)
        second_state.on_entry(entry_cb)
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_state(second_state)
        state_machine.add_event(event)
        state_machine.add_transition(initial_state, second_state, event)

        return state_machine

    def test_event_trigger_propagate_with_child_sm(self):
        state_machine = StateMachine("sm")
        exit_cb = MagicMock()
        entry_cb = MagicMock()
        initial_state = State("initial_state")
        second_state = State("second_state")
        initial_state.on_exit(exit_cb)
        second_state.on_entry(entry_cb)
        initial_state.set_child_sm(self.create_child_fsm())
        event = Event("event")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_state(second_state)
        state_machine.add_event(event)
        state_machine.add_transition(initial_state, second_state, event)
        state_machine.start("data")
        exit_cb.assert_not_called()
        entry_cb.assert_not_called()
        state_machine.trigger_event(event, "data", propagate=True)
        # child fsm in current state, so the event is caught in child fsm
        assert state_machine.current_state == initial_state
        assert initial_state.child_sm.current_state.name == \
               "child_second_state"

    def test_exit_callback(self):
        exit_sm_cb = MagicMock()
        state_machine = StateMachine("sm")
        state_machine.on_exit(exit_sm_cb)
        initial_state = State("initial_state")
        second_state = State("second_state")
        exit_state_error = ExitState("Error")
        event = Event("event")
        error_event = Event("error")
        state_machine.add_state(initial_state, initial_state=True)
        state_machine.add_state(second_state)
        state_machine.add_state(exit_state_error)
        state_machine.add_event(event)
        state_machine.add_event(error_event)
        state_machine.add_transition(initial_state, second_state, event)
        state_machine.add_transition(second_state, exit_state_error,
                                     error_event)
        state_machine.start("data")
        assert state_machine.current_state == initial_state
        state_machine.trigger_event(event, "data")
        assert state_machine.current_state == second_state
        state_machine.trigger_event(error_event, "data")
        assert state_machine.current_state == exit_state_error
        exit_sm_cb.assert_called_once_with(exit_state_error, "data")


class TestTransition:
    def test_normal_transition_constructor(self):
        source_state = State("source")
        destination_state = State("destination")
        event = Event("event")
        transition = NormalTransition(source_state, destination_state, event)
        assert transition.event == event
        assert transition.source_state == source_state
        assert transition.destination_state == destination_state

    def test_self_transition_constructor(self):
        source_state = State("source")
        event = Event("event")
        transition = SelfTransition(source_state, event)
        assert transition.event == event
        assert transition.source_state == source_state
        assert transition.destination_state == source_state

    def test_null_transition_constructor(self):
        source_state = State("source")
        event = Event("event")
        transition = NullTransition(source_state, event)
        assert transition.event == event
        assert transition.source_state == source_state
        assert transition.destination_state == source_state

    def test_normal_transition_no_condition(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        destination_state = State("destination")
        destination_state.on_entry(entry_callback)
        event = Event("event")
        transition = NormalTransition(source_state, destination_state, event)
        transition("data")
        entry_callback.assert_called_once_with("data")
        exit_callback.assert_called_once_with("data")

    def test_normal_transition_condition_true(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        destination_state = State("destination")
        destination_state.on_entry(entry_callback)
        event = Event("event")
        transition = NormalTransition(source_state, destination_state, event)
        condition_callback = MagicMock(return_value=True)
        transition.add_condition(condition_callback)
        transition("data")
        entry_callback.assert_called_once_with("data")
        exit_callback.assert_called_once_with("data")
        condition_callback.assert_called_once_with("data")

    def test_normal_transition_condition_false(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        destination_state = State("destination")
        destination_state.on_entry(entry_callback)
        event = Event("event")
        transition = NormalTransition(source_state, destination_state, event)
        condition_callback = MagicMock(return_value=False)
        transition.add_condition(condition_callback)
        transition("data")
        entry_callback.assert_not_called()
        exit_callback.assert_not_called()
        condition_callback.assert_called_once_with("data")

    def test_normal_transition_action(self):
        source_state = State("source")
        destination_state = State("destination")
        event = Event("event")
        transition = NormalTransition(source_state, destination_state, event)
        condition_callback = MagicMock(return_value=True)
        action_callback = MagicMock()
        transition.add_condition(condition_callback)
        transition.add_action(action_callback)
        transition("data")
        condition_callback.assert_called_once_with("data")
        action_callback.assert_called_once_with("data")

    def test_self_transition_no_condition(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        source_state.on_entry(entry_callback)
        event = Event("event")
        transition = SelfTransition(source_state, event)
        transition("data")
        entry_callback.assert_called_once_with("data")
        exit_callback.assert_called_once_with("data")

    def test_self_transition_condition_true(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        source_state.on_entry(entry_callback)
        event = Event("event")
        transition = SelfTransition(source_state, event)
        condition_callback = MagicMock(return_value=True)
        transition.add_condition(condition_callback)
        transition("data")
        entry_callback.assert_called_once_with("data")
        exit_callback.assert_called_once_with("data")
        condition_callback.assert_called_once_with("data")

    def test_self_transition_condition_false(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        source_state.on_entry(entry_callback)
        event = Event("event")
        transition = SelfTransition(source_state, event)
        condition_callback = MagicMock(return_value=False)
        transition.add_condition(condition_callback)
        transition("data")
        entry_callback.assert_not_called()
        exit_callback.assert_not_called()
        condition_callback.assert_called_once_with("data")

    def test_self_transition_action(self):
        source_state = State("source")
        event = Event("event")
        transition = SelfTransition(source_state, event)
        condition_callback = MagicMock(return_value=True)
        action_callback = MagicMock()
        transition.add_condition(condition_callback)
        transition.add_action(action_callback)
        transition("data")
        condition_callback.assert_called_once_with("data")
        action_callback.assert_called_once_with("data")

    def test_null_transition_no_condition(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        source_state.on_entry(entry_callback)
        event = Event("event")
        transition = NullTransition(source_state, event)
        transition("data")
        entry_callback.assert_not_called()
        exit_callback.assert_not_called()

    def test_null_transition_condition_true(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        source_state.on_entry(entry_callback)
        event = Event("event")
        transition = NullTransition(source_state, event)
        condition_callback = MagicMock(return_value=True)
        transition.add_condition(condition_callback)
        transition("data")
        entry_callback.assert_not_called()
        exit_callback.assert_not_called()
        condition_callback.assert_called_once_with("data")

    def test_null_transition_condition_false(self):
        entry_callback = MagicMock()
        exit_callback = MagicMock()
        source_state = State("source")
        source_state.on_exit(exit_callback)
        source_state.on_entry(entry_callback)
        event = Event("event")
        transition = NullTransition(source_state, event)
        condition_callback = MagicMock(return_value=False)
        transition.add_condition(condition_callback)
        transition("data")
        entry_callback.assert_not_called()
        exit_callback.assert_not_called()
        condition_callback.assert_called_once_with("data")

    def test_null_transition_action(self):
        source_state = State("source")
        event = Event("event")
        transition = NullTransition(source_state, event)
        condition_callback = MagicMock(return_value=True)
        action_callback = MagicMock()
        transition.add_condition(condition_callback)
        transition.add_action(action_callback)
        transition("data")
        condition_callback.assert_called_once_with("data")
        action_callback.assert_called_once_with("data")
