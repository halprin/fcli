import click
from ..jira import tasks
from requests.exceptions import HTTPError
from ..auth.combo import ComboAuth


issue_url = 'https://jira.cms.gov/rest/api/2/issue/'

# initial key is the start status
# then get either 'Backlog' or 'Triage' depending upon what type of task we're moving
# then look for the end state
# the list associated to the end state are the ids for the state transitions to make
#
# Triage workflow
# Triage -> Ready (11)
# Ready -> In Progress (21)
# In Progress -> Closed (31)
# In Progress -> Ready (61)
# In Progress -> Blocked (71)
# Blocked -> In Progress (81)
# Closed -> Triage (41)
# Closed -> In Progress (51)
#
# Backlog workflow
# Open -> Resolved (21)
# Open -> Closed (31)
# Open -> Ready for Refinement (201)
# In Progress -> Open (41)
# In Progress -> Closed (61)
# In Progress -> Blocked (241)
# In Progress -> Socialize (261)
# In Progress -> Ready (291)
# In Progress -> Resolved (51)
# Resolved -> Closed (71)
# Resolved -> Verified (81)
# Resolved -> Reopened (91)
# Verified -> Closed (101)
# Verified -> Ready to Deploy (121)
# Verified -> Reopened (191)
# Ready to Deploy -> Closed (131)
# Ready to Deploy -> Reopened (141)
# Reopened -> Closed (161)
# Reopened -> In Progress (171)
# Reopened -> Resolved (51)
# Closed -> Reopened (181)
# Ready for Refinement -> Refined (211)
# Ready for Refinement -> Needs Work (231)
# Refined -> Ready (221)
# Refined -> Needs Work (231)
# Needs Work -> Ready for Refinement (201)
# Ready -> In Progress (11)
# Ready -> Needs Work (231)
# Blocked -> In Progress (251)
# Socialize -> In Progress (271)
# Socialize -> Resolved (281)
transition_dict = {
    'Open': {'Backlog': {'Resolved': [21],  # Open -> Resolved
                         'Closed': [31],  # Open -> Closed
                         'Ready for Refinement': [201],  # Open -> RfR
                         'In Progress': [201, 211, 221, 11],  # Open -> RfR -> Refined -> Ready -> In Progress
                         'Needs Work': [201, 231],  # Open -> RfR -> Needs Work
                         'Refined': [201, 211],  # Open -> RfR -> Refined
                         'Ready': [201, 211, 221],  # Open -> RfR -> Refined -> Ready
                         'Blocked': [201, 211, 221, 11, 241],  # Open -> RfR -> Refined -> Ready -> IP -> Blocked
                         'Socialize': [201, 211, 221, 11, 261]},  # Open -> RfR -> Ref -> Ready -> IP -> Social
             'Triage': None
            },
    'Ready for Refinement': {'Backlog': {'Resolved': [211, 221, 11, 51],  # RfR -> Refined -> Ready -> IP -> Resolved
                                         'Closed': [211, 221, 11, 61],  # RfR -> Refined -> Ready -> IP -> Closed
                                         'Open': [211, 221, 11, 41],  # RfR -> Refined -> Ready -> In Progress -> Open
                                         'In Progress': [211, 221, 11],  # RfR -> Refined -> Ready -> In Progress
                                         'Needs Work': [231],  # RfR -> Needs Work
                                         'Refined': [211],  # RfR -> Refined
                                         'Ready': [211, 221],  # RfR -> Refined -> Ready
                                         'Blocked': [211, 221, 11, 241],  # RfR -> Refined -> Ready -> IP -> Block
                                         'Socialize': [211, 221, 11, 261]},  # RfR -> Ref -> Ready -> IP -> Social
                             'Triage': None},
    'Needs Work': {'Backlog': {'Resolved': [201, 211, 221, 11, 51],  # NW -> RfR -> Refined -> Ready -> IP -> Res
                               'Closed': [201, 211, 221, 11, 61],  # NW -> RfR -> Refined -> Ready -> IP -> Closed
                               'Open': [201, 211, 221, 11, 41],  # NW -> RfR -> Refined -> Ready -> IP -> Open
                               'In Progress': [201, 211, 221, 11],  # Needs Work -> RfR -> Refined -> Ready -> IP
                               'Ready for Refinement': [201],  # Needs Work -> RfR
                               'Refined': [201, 211],  # Needs Work -> RfR -> Refined
                               'Ready': [201, 211, 221],  # Needs Work -> RfR -> Refined -> Ready
                               'Blocked': [201, 211, 221, 11, 241],  # NW -> RfR -> Ref -> Ready -> IP -> Blocked
                               'Socialize': [201, 211, 221, 11, 261]},  # NW -> RfR -> Ref -> Ready -> IP -> Soc
                   'Triage': None},
    'Refined': {'Backlog': {'Resolved': [221, 11, 51],  # Refined -> Ready -> In Progress -> Resolved
                            'Closed': [221, 11, 61],  # Refined -> Ready -> In Progress -> Closed
                            'Open': [221, 11, 41],  # Refined -> Ready -> In Progress -> Open
                            'In Progress': [221, 11],  # Refined -> Ready -> In Progress
                            'Needs Work': [231],  # Refined -> Needs Work
                            'Ready for Refinement': [231, 201],  # Refined -> Needs Work -> RfR
                            'Ready': [221],  # Refined -> Ready
                            'Blocked': [221, 11, 241],  # Refined -> Ready -> In Progress -> Blocked
                            'Socialize': [221, 11, 261]},  # Refined -> Ready -> In Progress -> Socialize
                'Triage': None},
    'Ready': {'Backlog': {'Resolved': [11, 51],  # Ready -> In Progress -> Resolved
                          'Closed': [11, 61],  # Ready -> In Progress -> Closed
                          'Open': [11, 41],  # Ready -> In Progress -> Open
                          'In Progress': [11],  # Ready -> In Progress
                          'Needs Work': [231],  # Ready -> Needs Work
                          'Ready for Refinement': [231, 201],  # Ready -> Needs Work -> RfR
                          'Refined': [231, 201, 211],  # Ready -> Needs Work -> RfR -> Refined
                          'Blocked': [11, 241],  # Ready -> In Progress -> Blocked
                          'Socialize': [11, 261]},  # Ready -> In Progress -> Socialize
              'Triage': {'Triage': [21, 31, 41],
                         'In Progress': [21],
                         'Closed': [21, 31],
                         'Blocked': [21, 71]}},
    'In Progress': {'Backlog': {'Resolved': [51],  # In Progress -> Resolved
                                'Closed': [61],  # In Progress -> Closed
                                'Open': [41],  # In Progress -> Open
                                'Ready': [291],  # In Progress -> Ready
                                'Needs Work': [291, 231],  # In Progress -> Ready -> Needs Work
                                'Ready for Refinement': [291, 231, 201],  # In Progress -> Ready -> Needs Work -> RfR
                                'Refined': [291, 231, 201, 211],  # In Progress -> Ready -> Needs Work -> RfR -> Refined
                                'Blocked': [241],  # In Progress -> Blocked
                                'Socialize': [261]},  # In Progress -> Socialize
                    'Triage': {'Triage': [31, 41],
                               'Ready': [61],
                               'Closed': [31],
                               'Blocked': [71]}},
    'Blocked': {'Backlog': {'Resolved': [251, 51],  # Blocked -> In Progress -> Resolved
                            'Closed': [251, 61],  # Blocked -> In Progress -> Closed
                            'Open': [251, 41],  # Blocked -> In Progress -> Open
                            'Ready': [251, 291],  # Blocked -> In Progress -> Ready
                            'Needs Work': [251, 291, 231],  # Blocked -> In Progress -> Ready -> Needs Work
                            'Ready for Refinement': [251, 291, 231, 201],  # Block -> IP -> Ready -> Needs Work -> RfR
                            'Refined': [251, 291, 231, 201, 211],  # Block -> IP -> Ready -> NW -> RfR -> Refined
                            'In Progress': [251],  # Blocked -> In Progress
                            'Socialize': [251, 261]},  # Blocked -> In Progress -> Socialize
                'Triage': {'Triage': [81, 31, 41],
                           'Ready': [81, 61],
                           'In Progress': [81],
                           'Closed': [81, 31]}},
    'Socialize': {'Backlog': {'Resolved': [281],  # Socialize -> Resolved
                              'Closed': [281, 71],  # Socialize -> Resolved -> Closed
                              'Open': [271, 41],  # Socialize -> In Progress -> Open
                              'Ready': [271, 291],  # Socialize -> In Progress -> Ready
                              'Needs Work': [271, 291, 231],  # Socialize -> In Progress -> Ready -> Needs Work
                              'Ready for Refinement': [271, 291, 231, 201],  # Socialize -> IP -> Ready -> NW -> RfR
                              'Refined': [271, 291, 231, 201, 211],  # Socialize -> IP -> Ready -> NW -> RfR -> Refined
                              'In Progress': [271],  # Socialize -> In Progress
                              'Blocked': [271, 241]},  # Socialize -> In Progress -> Blocked
                  'Triage': None},
    'Closed': {'Backlog': {'Resolved': [181, 51],  # Closed -> Reopened -> Resolved
                           'Socialize': [181, 171, 261],  # Closed -> Reopened -> In Progress -> Socialize
                           'Open': [181, 171, 41],  # Closed -> Reopened -> In Progress -> Open
                           'Ready': [181, 171, 291],  # Closed -> Reopened -> In Progress -> Ready
                           'Needs Work': [181, 171, 291, 231],  # Closed -> Reopened -> IP -> Ready -> Needs Work
                           'Ready for Refinement': [181, 171, 291, 231, 201],  # Cl -> Reo -> IP -> Ready -> NW -> RfR
                           'Refined': [181, 171, 291, 231, 201, 211],  # Cl -> Reo -> IP -> Read -> NW -> RfR -> Ref
                           'In Progress': [181, 171],  # Closed -> Reopened -> In Progress
                           'Blocked': [181, 171, 241]},  # Closed -> Reopened -> In Progress -> Blocked
               'Triage': {'Triage': [41],
                          'Ready': [51, 61],
                          'In Progress': [51],
                          'Blocked': [51, 71]}},
    'Reopened': {'Backlog': {'Resolved': [51],  # Reopened -> Resolved
                             'Socialize': [171, 261],  # Reopened -> In Progress -> Socialize
                             'Open': [171, 41],  # Reopened -> In Progress -> Open
                             'Ready': [171, 291],  # Reopened -> In Progress -> Ready
                             'Needs Work': [171, 291, 231],  # Reopened -> IP -> Ready -> Needs Work
                             'Ready for Refinement': [171, 291, 231, 201],  # Reo -> IP -> Ready -> NW -> RfR
                             'Refined': [171, 291, 231, 201, 211],  # Reo -> IP -> Read -> NW -> RfR -> Ref
                             'In Progress': [171],  # Reopened -> In Progress
                             'Blocked': [171, 241],  # Reopened -> In Progress -> Blocked
                             'Closed': [161]},  # Reopened -> Closed
                 'Triage': None},
    'Triage': {'Backlog': None,
               'Triage': {'Ready': [11],
                          'In Progress': [11, 21],
                          'Closed': [11, 21, 31],
                          'Blocked': [11, 21, 71]}}
}


@click.group()
def task():
    pass


@task.command()
@click.option('--username')
@click.argument('task_id')
@click.argument('state')
def move(username: str, task_id: str, state: str):
    click.echo('Transitioning task')

    auth = ComboAuth(username)

    try:
        # use a factory method to GET the issue by key
        the_task = tasks.get_task(issue_url, task_id, auth)

    except HTTPError as exception:
        click.echo('Task search failed with {}'.format(exception))

    # use created Task (could be Backlog task or Triage task) to transition to desired state
    # Look up starting state in dictionary
    # then look up task type (Backlog or Triage)
    # then look up end state
    # array is the sequence of state transitions in order to iterate through

    transition_arr = transition_dict[the_task.state][the_task.type_str()][state]

    if transition_arr is None:
        click.echo('Unable to find a transition path from {} to {}'.format(the_task.state, state))
    else:
        try:
            print('transitions: {}'.format(transition_arr))
            for transition_id in transition_arr:
                the_task._transition(transition_id)

        except HTTPError as exception:
            click.echo('Failure to complete transition path: {}'.format(exception))

    click.echo('Successfully transitioned {} to state {}'.format(task_id, state))