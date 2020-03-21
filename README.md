# [MC921] Project 1 - Scanner and Parser
The goal of the first project is to implement a scanner, and a parser for the uC
language, specified by [uC BNF Grammar].

## Resources

Study the specification of uC grammar carefully. To complete this first project,
you will use the [PLY](http://www.dabeaz.com/ply/), a Python version of the
[lex/yacc](http://dinosaur.compilertools.net/) toolset with same functionality
but with a friendlier interface

## Set up the virtual environment
First and foremost, before running the project, one should setup the virtual
environment. For this project we use **Pipenv** as the package manager. To
install it just run the command:

```bash
$ pip3 install pipenv
```

And then to start a virtual environment just run this command:

```bash
$ pipenv shell
```

## Install all requirements
After setting up the virtual environment, all required module should be
installed with this command:

```bash
$ pipenv install
```

## Testing a basic lex
To check if everything was done correctly, run this command inside the virtual
env to run all tests:

```bash
$ pipenv run tests
```

All tests should run and pass.
