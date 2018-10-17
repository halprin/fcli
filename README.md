# FCLI Foundational Components CLI
Helps spread the AwesomeSauce of the Foundational Components team a bit further.

## Prerequisites
[Python 3](https://www.python.org/downloads/) is required.  Python 2 is not supported.

Second, Python 3's `bin` directory needs to be in your `PATH` environment variable.  For example, on macOS, you will
need to add the following to your `~/.profile`.
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

### Task Administration
There are two types of task the `fcli` can add: triage tasks and backlog tasks.

To add a triage task,
```bash
$ fcli task "<task title>" "<task description>" [--in-progress] [--no-assign]
```

A new task is created in the triage board with the specified title and description.  Optionally, put the task into the
In Progress state with the `--in-progress` option, and optionally do not automatically assign the task to yourself with
`--no-assign`.

To add a backlog task,
```bash
$ fcli task "<task title>" "<task description>" <parent story>
```

A new task is created in the standard backlog with the specified title and description.  The task is linked with
the parent story.  If the parent story is already in an active sprint, the task is also moved into the same sprint.

## Development
I accept PRs!  Check out the [issues](https://github.com/halprin/fcli/issues) and assign yourself when you start
working on one.
