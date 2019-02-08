# FCLI Foundational Components CLI
Helps spread the AwesomeSauce of the Foundational Components team a bit further.

## Prerequisites
[Python 3](https://www.python.org/downloads/) is required.  Python 2 is not supported.

Second, Python 3's `bin` directory needs to be in your `PATH` environment variable.  For example, if you are using the
python.org install on macOS, you will need to add the following to your `~/.profile`.
```bash
PATH="/Library/Frameworks/Python.framework/Versions/3.*/bin:${PATH}"
```

## Installation
`fcli` is located on [PyPI](https://pypi.org/project/fcli/).

To install, run the following.
```bash
$ pip3 install fcli
```

`sudo` may be needed if your Python 3 installation is in a protected directory.  This will put the command the `bin`
directory of your Python 3 installation.

To update `fcli` to the latest version, run the following.
```bash
$ pip3 install --upgrade fcli
```

Again, `sudo` may be required.

## Specifying Credentials
`fcli` uses your EUA credentials to authenticate yourself to JIRA, etc.  There are multiple ways to specify your
credentials.

### File
Create an ini file at `~/.fcli`.  In there, add the `[default]` section, and under that section specify a `username` and
`password`.  An example can be seen in [fcli.ini](./fcli.ini).

### Environment Variables
The environment variables `FCLI_USER` and `FCLI_PASS` can be utilized to specify the username and password.

### CLI
Only the `username` can be specified via the CLI.  Tack on the `--username <username>` option.

### Keyboard
If the username or password is not specified in some other fashion, the CLI will prompt the user.

## Usage

### Story Administration

#### Story Creation

To create a story in the backlog use
```bash
$ fcli backlog create story '<story title>'
```

You will be prompted to enter a Description and Acceptance Criteria.

### Task Administration

#### Task Creation

There are three types of tasks the `fcli` can add: triage, EL, and backlog tasks.

To add a triage task,
```bash
$ fcli triage create "<task title>" "<task description>"  [--importance <High/Medium/Low>] [--effort <High/Medium/Low>] [--due <date in the future>] [--in-progress] [--assign]
```

A new task is created in the triage board with the specified title and description.  Optionally, put the task into the
In Progress state with the `--in-progress` option, and optionally assign the task to yourself with
`--assign`.  The importance, effort, and due date are required, and they will be prompted for if they are not
supplied on the command line.

To add an EL task,
```bash
$ fcli el create "<task title>" "<task description>"  [--importance <High/Medium/Low>] [--effort <High/Medium/Low>] [--due <date in the future>] [--in-progress] [--assign]
```

A new task is created in the EL board with the specified title and description.  EL tasks require the same options as
triage tasks.  

To add a backlog task,
```bash
$ fcli backlog create task "<task title>" "<task description>" <parent story>
```

A new task is created in the standard backlog with the specified title and description.  The task is linked with
the parent story.  If the parent story is already in an active sprint, the task is also moved into the same sprint.

#### Other Task Functions

To move a task from one status to another...
```bash
$ fcli task move <task key> <target status>
```

To run the triage and EL task scoring process...
```bash
$ fcli task score
```

#### Other Backlog Functions

To add a calculated VFR value to a story in the backlog and move it to Refined status...
```bash
$ fcli backlog score <task key> <duration> <cost of delay>
```

#### Triage Task Administration

There are currently two different tasks for triage administration: search for all open triage tasks and update the score for all open triage tasks.

To search for all open triage tasks,
```bash
$ fcli triage search
```

A json representation of all of the open triage tasks will be printed to the terminal.

The scores of all open triage tasks will be updated. The terminal will show progress.

## Development
I accept PRs!  Check out the [issues](https://github.com/halprin/fcli/issues) and assign yourself when you start
working on one.
