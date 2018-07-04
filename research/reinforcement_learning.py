#!/usr/bin/env python3
"""Reinforcement learning agents and environments."""

from collections import defaultdict
from copy import copy

from .randommixin import RandomMixin


class Environment:
    """A reinforcement learning environment."""

    def get_state(self):
        """Get the current state.

        This is different from get_observation() in that the state includes
        otherwise hidden information that the agent may not have access to. As
        a rule, the state should be sufficient to completely reconstruct the
        environment. (Although this may not always be necessary, with a random
        seed for example.)

        Returns:
            State: The state, or None if at the end of an episode
        """
        raise NotImplementedError()

    def get_observation(self):
        """Get the current observation.

        See note on get_state() for the difference between the methods.

        Returns:
            State: The observation as a State, or None if the episode has ended
        """
        raise NotImplementedError()

    def get_actions(self):
        """Get the available actions.

        Returns:
            [Action]: A list of available actions.
        """
        raise NotImplementedError()

    def end_of_episode(self):
        """Determine if the episode has ended.

        Returns:
            bool: True if the episode has ended.
        """
        return self.get_actions() == []

    def reset(self):
        """Reset the environment entirely.

        The result of calling this method should have the same effect as
        creating a new environment from scratch. Use start_new_episode() to reset the
        environment for a new episode.
        """
        raise NotImplementedError()

    def start_new_episode(self):
        """Reset the environment for a new episode.

        See note on reset() for the difference between the methods.
        """
        raise NotImplementedError()

    def react(self, action):
        """Update the environment to an agent action.

        Assumes the argument is one of the returned actions from get_actions().

        Arguments:
            action (Action): The action the agent took

        Returns:
            float: The reward for the agent for the previous action.
        """
        raise NotImplementedError()

    def visualize(self):
        """Create visualization of the environment.

        Returns:
            str: A visualization of the current state.
        """
        raise NotImplementedError()


class AttrDict:
    """A read-only dictionary that provides named-member access.

    This class acts as a read-only dictionary, but that also provides named-
    member access. Once initialized, the contents of the dictionary cannot
    be changed. In practice, could be used to create one-off objects that do
    not conform to any template (unlike collections.namedtuple).

    Examples:
        >>> ad = AttrDict(name="test", num=2)
        >>> ad['name']
        'test'
        >>> ad.name
        'test'
        >>> ad['num']
        2
        >>> ad.num
        2
    """

    def __init__(self, **kwargs):
        """Construct an AttrDict object.

        Arguments:
            **kwargs: Arbitrary key-value pairs
        """
        self._attributes_ = kwargs

    def __iter__(self):
        return self._attributes_.items().__iter__()

    def __getattr__(self, name):
        if name in self._attributes_:
            return self._attributes_[name]
        else:
            raise AttributeError('class {} has no attribute {}'.format(type(self).__name__, name))

    def __getitem__(self, key):
        return self._attributes_[key]

    def __hash__(self):
        return hash(tuple(sorted(self._attributes_.items())))

    def __eq__(self, other):
        # pylint: disable=protected-access
        return type(self) is type(other) and self._attributes_ == other._attributes_

    def __str__(self):
        return '{}({})'.format(
            type(self).__name__,
            ', '.join('{}={}'.format(*kv) for kv in sorted(self)),
        )

    def __repr__(self):
        return str(self)

    def as_dict(self):
        """Convert to dict.

        Returns:
            dict[str, any]: The internal dictionary.
        """
        return copy(self._attributes_)


class Action(AttrDict):
    """An action in a reinforcement learning environment."""

    def __init__(self, name, **kwargs):
        """Construct an Action object.

        Arguments:
            name (str): The name of the Action
            **kwargs: Arbitrary key-value pairs
        """
        super().__init__(**kwargs)
        self.name = name

    def __hash__(self):
        return hash(tuple([self.name, *sorted(self)]))

    def __str__(self):
        return 'Action("{}", {})'.format(
            self.name,
            ', '.join('{}={}'.format(*kv) for kv in sorted(self)),
        )


class State(AttrDict):
    """A state or observation in a reinforcement learning environment."""

    pass


class Agent(RandomMixin):
    """A reinforcement learning agent."""

    def __init__(self, *args, **kwargs):
        """Initialize the Agent.

        Arguments:
            *args: Arbitrary positional arguments.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.prev_observation = None
        self.prev_action = None
        self.start_new_episode()

    def start_new_episode(self):
        """Prepare the agent for a new episode."""
        self.prev_observation = None
        self.prev_action = None

    def observe_reward(self, observation, reward):
        """Update the value function with the reward.

        Arguments:
            observation (State): The current observation.
            reward (float): The reward from the previous action.
        """
        raise NotImplementedError()

    def get_value(self, observation, action):
        """Get the Q value for an action at an observation.

        Arguments:
            observation (State): The observation
            action (Action): The action

        Returns:
            float: The value for the action at the observation.
        """
        raise NotImplementedError()

    def get_stored_actions(self, observation):
        """Get all actions with stored values at an observation.

        Arguments:
            observation (State): The observation.

        Returns:
            Sequence[Action]: The stored actions at the observation.
        """
        raise NotImplementedError()

    def get_best_action(self, observation):
        """Get the action with the highest value at an observation.

        Arguments:
            observation (State): The observation.

        Returns:
            Action: The best action for the given observation.
        """
        actions = self.get_stored_actions(observation)
        if not actions:
            return None
        else:
            return max(actions, key=(lambda action: self.get_value(observation, action)))

    def get_best_value(self, observation):
        """Get the highest value at an observation.

        Arguments:
            observation (State): The observation.

        Returns:
            float: The value of the best action for the given observation.
        """
        return self.get_value(observation, self.get_best_action(observation))

    def act(self, observation, actions):
        """Update the value function and decide on the next action.

        Arguments:
            observation (State): The observation of the environment.
            actions (list[Action]): List of available actions.

        Returns:
            Action: The action the agent takes.
        """
        best_action = self.get_best_action(observation)
        if best_action is None:
            best_action = self.rng.choice(actions)
        return self.force_act(observation, best_action)

    def force_act(self, observation, action):
        """Update the value function and return a specific action.

        Arguments:
            observation (State): The observation of the environment.
            action (list[Action]): The action to return.

        Returns:
            Action: The action the agent takes.
        """
        self.prev_observation = observation
        if observation is None:
            self.prev_action = None
        else:
            self.prev_action = action
        return action

    def print_value_function(self):
        """Print the value function."""
        raise NotImplementedError()


class TabularQLearningAgent(Agent):
    """A tabular Q-learning reinforcement learning agent."""

    def __init__(self, learning_rate, discount_rate, *args, **kwargs):
        """Construct a tabular Q-learning agent.

        Arguments:
            learning_rate (float): The learning rate (alpha).
            discount_rate (float): The discount rate (gamma).
            *args: Arbitrary positional arguments.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.value_function = defaultdict((lambda: defaultdict(float)))
        self.learning_rate = learning_rate
        self.discount_rate = discount_rate

    def get_value(self, observation, action): # noqa: D102
        if observation not in self.value_function:
            return 0
        return self.value_function[observation][action]

    def get_stored_actions(self, observation): # noqa: D102
        if observation not in self.value_function:
            return []
        return self.value_function[observation].keys()

    def observe_reward(self, observation, reward): # noqa: D102
        prev_value = self.get_value(self.prev_observation, self.prev_action)
        next_value = reward + self.discount_rate * self.get_best_value(observation)
        new_value = (1 - self.learning_rate) * prev_value + self.learning_rate * next_value
        self.value_function[self.prev_observation][self.prev_action] = new_value

    def print_value_function(self): # noqa: D102
        for state, values in sorted(self.value_function.items(), key=(lambda kv: str(kv[0]))):
            print(state)
            for action, value in sorted(values.items(), key=(lambda kv: str(kv[1]))):
                print('    {}: {:.3f}'.format(action, value))


def epsilon_greedy(cls):
    """Decorate an Agent to be epsilon-greedy.

    This decorator function takes a class (and a value of epsilon) and, on the
    fly, creates a subclass which acts in an epsilon-greedy manner.
    Specifically, it overrides Agent.act() to select a random action with
    epsilon probability.

    Arguments:
        cls (class): The Agent superclass.

    Returns:
        class: An Agent subclass that behaves epsilon greedily.
    """
    assert issubclass(cls, Agent)

    class EpsilonGreedyMetaAgent(cls):
        """A subclass to make an Agent epsilon greedy."""

        # pylint: disable = missing-docstring

        def __init__(self, exploration_rate, *args, **kwargs): # noqa: D102
            """Initialize the epsilon-greedy agent.

            Arguments:
                exploration_rate (float): The probability of random action.
                *args: Arbitrary positional arguments.
                **kwargs: Arbitrary keyword arguments.
            """
            super().__init__(*args, **kwargs)
            self.exploration_rate = exploration_rate

        def act(self, observation, actions, reward=None): # noqa: D102
            if not actions:
                self.observe_reward(observation, reward)
                return None
            elif self.rng.random() < self.exploration_rate:
                return self.force_act(observation, self.rng.choice(actions))
            else:
                return self.act(observation, actions, reward)

    return EpsilonGreedyMetaAgent


class GridWorld(Environment):
    """A simple, obstacle-free GridWorld environment."""

    def __init__(self, width, height, start, goal):
        """Construct the GridWorld.

        Arguments:
            width (int): The width of the grid.
            height (int): The height of the grid.
            start (list[int]): The starting location. Origin is top left.
            goal (list[int]): The goal location. Origin is top left.
        """
        self.width = width
        self.height = height
        self.start = list(start)
        self.goal = list(goal)
        self.row = start[0]
        self.col = start[1]

    def get_state(self): # noqa: D102
        return State(row=self.row, col=self.col)

    def get_observation(self): # noqa: D102
        return self.get_state()

    def get_actions(self): # noqa: D102
        if [self.row, self.col] == self.goal:
            return []
        actions = []
        if self.row > 0:
            actions.append(Action('up'))
        if self.row < self.height - 1:
            actions.append(Action('down'))
        if self.col > 0:
            actions.append(Action('left'))
        if self.col < self.width - 1:
            actions.append(Action('right'))
        return actions

    def reset(self): # noqa: D102
        self.start_new_episode()

    def start_new_episode(self): # noqa: D102
        self.row = self.start[0]
        self.col = self.start[1]

    def react(self, action=None): # noqa: D102
        assert action in self.get_actions()
        if action.name == 'up':
            self.row = max(0, self.row - 1)
        elif action.name == 'down':
            self.row = min(self.height - 1, self.row + 1)
        elif action.name == 'left':
            self.col = max(0, self.col - 1)
        elif action.name == 'right':
            self.col = min(self.width - 1, self.col + 1)
        if [self.row, self.col] == self.goal:
            return 1
        else:
            return -1

    def visualize(self): # noqa: D102
        raise NotImplementedError


def augment_state(state, memories, prefix):
    """Add memory items to states and observations.

    Note that we need to remove existing 'memory_' attributes because
    super().get_state() could call the overridden get_observation().

    Arguments:
        state (State): The state to augment.
        memories (list): The memories to augment with.
        prefix (str): The prefix to use for memories.

    Returns:
        State: The state with memory items.
    """
    state = state.as_dict()
    for key in list(state.keys()):
        if key.startswith(prefix):
            del state[key]
    memories = {(prefix + '{}'.format(i)): value for i, value in enumerate(memories)}
    return State(**memories, **state)


def gating_memory(cls, num_memory_slots=1, reward=0):
    """Decorate an Environment to include a gating memory.

    This decorator function takes a class (and some parameters) and, on the
    fly, creates a subclass with additional "memory" elements. Specifically, it
    augments the observation with additional attributes, which the agent can
    use as part of its state. The subclass also provides an additional "gate"
    action which the agent can use to change the contents of memory.

    Since the gating of memory is an "internal" action, a different reward may
    be given for the "gate" action.

    Arguments:
        cls (class): The Environment superclass.
        num_memory_slots (int): The amount of memory. Defaults to 1.
        reward (float): The reward for an internal action. Defaults to 0.

    Returns:
        class: A subclass with a gating memory.
    """
    assert issubclass(cls, Environment)

    class GatingMemoryMetaEnvironment(cls):
        """A subclass to add a gating memory to an Environment."""

        # pylint: disable = missing-docstring

        ATTR_PREFIX = 'memory_'

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.reward = reward
            self.memories = num_memory_slots * [None]

        def get_state(self):
            state = super().get_state()
            if state is None:
                return None
            return augment_state(state, self.memories, self.ATTR_PREFIX)

        def get_observation(self):
            observation = super().get_observation()
            if observation is None:
                return None
            return augment_state(observation, self.memories, self.ATTR_PREFIX)

        def get_actions(self):
            actions = super().get_actions()
            if actions == []:
                return actions
            observations = super().get_observation()
            if observations is None:
                return actions
            for slot_num in range(len(self.memories)):
                for attr, _ in observations:
                    if attr.startswith(self.ATTR_PREFIX):
                        continue
                    actions.append(Action('gate', slot=slot_num, attribute=attr))
            return actions

        def reset(self):
            super().reset()
            self.memories = len(self.memories) * [None]

        def start_new_episode(self):
            super().start_new_episode()
            self.memories = len(self.memories) * [None]

        def react(self, action):
            if action.name == 'gate':
                self.memories[action.slot] = getattr(super().get_observation(), action.attribute)
                return self.reward
            else:
                return super().react(action)

    return GatingMemoryMetaEnvironment


def fixed_long_term_memory(cls, num_wm_slots=1, num_ltm_slots=1, reward=0):
    """Decorate an Environment to include a long-term memory of fixed size.

    Arguments:
        cls (class): The Environment superclass.
        num_wm_slots (int): The amount of working memory. Defaults to 1.
        num_ltm_slots (int): The amount of long-term memory. Defaults to 1.
        reward (float): The reward for an internal action. Defaults to 0.

    Returns:
        class: A subclass with a fixed-sized long-term memory.
    """
    assert issubclass(cls, Environment)

    class LongTermMemoryMetaEnvironment(cls):
        """A subclass to add a long-term memory to an Environment."""

        # pylint: disable = missing-docstring

        WM_PREFIX = 'wm_' # pylint: disable=invalid-name
        LTM_PREFIX = 'ltm_' # pylint: disable=invalid-name

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.reward = reward
            self.wm = num_wm_slots * [None] # pylint: disable=invalid-name
            self.ltm = num_ltm_slots * [None]

        def get_state(self):
            state = super().get_state()
            if state is None:
                return None
            state = augment_state(state, self.wm, self.WM_PREFIX)
            state = augment_state(state, self.ltm, self.LTM_PREFIX)
            return state

        def get_observation(self):
            observation = super().get_observation()
            if observation is None:
                return None
            return augment_state(observation, self.wm, self.WM_PREFIX)

        def get_actions(self):
            actions = super().get_actions()
            if actions == []:
                return actions
            observations = super().get_observation()
            if observations is None:
                return actions
            for slot_num in range(len(self.ltm)):
                for attr, _ in observations:
                    if attr.startswith(self.WM_PREFIX):
                        continue
                    actions.append(Action('store', slot=slot_num, attribute=attr))
            for wm_slot_num in range(len(self.wm)):
                for ltm_slot_num in range(len(self.ltm)):
                    actions.append(Action('retrieve', wm_slot=wm_slot_num, ltm_slot=ltm_slot_num))
            return actions

        def reset(self):
            super().reset()
            self.wm = len(self.wm) * [None]
            self.ltm = len(self.ltm) * [None]

        def start_new_episode(self):
            super().start_new_episode()
            self.wm = len(self.wm) * [None]
            self.ltm = len(self.ltm) * [None]

        def react(self, action):
            if action.name == 'store':
                self.ltm[action.slot] = getattr(super().get_observation(), action.attribute)
                return self.reward
            elif action.name == 'retrieve':
                self.wm[action.wm_slot] = self.ltm[action.ltm_slot]
                return self.reward
            else:
                return super().react(action)

    return LongTermMemoryMetaEnvironment


class SimpleTMaze(Environment, RandomMixin):
    """A T-maze environment, with hints on which direction to go."""

    def __init__(self, length, hint_pos, goal_x=0, **kwargs):
        """Construct the TMaze.

        Arguments:
            length (int): The length of the hallway before the choice point.
            hint_pos (int): The location of the hint.
            goal_x (int): The location of the goal. Must be -1 or 1. If left
                to default of 0, goal_x is chosen at random.
            **kwargs: Arbitrary keyword arguments.
        """
        assert 0 <= hint_pos < length
        super().__init__(**kwargs)
        self.length = length
        self.hint_pos = hint_pos
        self.x = 0
        self.y = 0
        self.init_goal_x = goal_x
        self.goal_x = 0 # dummy value

    def get_state(self): # noqa: D102
        observation = self.get_observation()
        return State(goal_x=self.goal_x, **observation.as_dict())

    def get_observation(self): # noqa: D102
        if self.y == self.hint_pos:
            return State(x=self.x, y=self.y, symbol=self.goal_x)
        return State(x=self.x, y=self.y, symbol=0)

    def get_actions(self): # noqa: D102
        actions = []
        if self.x == 0:
            if self.y < self.length:
                actions.append(Action('up'))
            elif self.y == self.length:
                actions.append(Action('left'))
                actions.append(Action('right'))
        return actions

    def reset(self): # noqa: D102
        self.start_new_episode()

    def start_new_episode(self): # noqa: D102
        self.x = 0
        self.y = 0
        if self.init_goal_x == 0:
            self.goal_x = self.rng.choice([-1, 1])
        else:
            self.goal_x = self.init_goal_x

    def react(self, action): # noqa: D102
        assert action in self.get_actions()
        if action.name == 'up':
            self.y += 1
        elif action.name == 'right':
            self.x += 1
        elif action.name == 'left':
            self.x -= 1
        if self.y == self.length:
            if self.x == self.goal_x:
                return 10
            elif self.x == -self.goal_x:
                return -10
            else:
                return -1
        elif action.name == 'gate':
            return -0.050
        else:
            return -1

    def visualize(self): # noqa: D102
        lines = []
        for _ in range(self.length + 1):
            lines.append([' ', '_', ' '])
        lines[0][1 + self.goal_x] = '$'
        lines[0][1 - self.goal_x] = '#'
        lines[self.length - self.y][1] = '*'
        lines[self.length - self.hint_pos][1] = '!'
        return '\n'.join(''.join(line) for line in lines)


def run_episodes(env, agent, num_episodes):
    """Print out a run of an Agent in an Environment.

    Arguments:
        env (Environment): The environment.
        agent (Agent): The agent.
        num_episodes (int): The number of episodes to run.

    Returns:
        List[float]: The returns of each episode.
    """
    returns = []
    for _ in range(num_episodes):
        env.start_new_episode()
        agent.start_new_episode()
        episodic_return = 0
        reward = None
        step = 0
        obs = env.get_observation()
        actions = env.get_actions()
        while not env.end_of_episode():
            action = agent.act(obs, actions)
            reward = env.react(action)
            obs = env.get_observation()
            agent.observe_reward(obs, reward)
            actions = env.get_actions()
            episodic_return += reward
            step += 1
        returns.append(episodic_return)
    return returns
