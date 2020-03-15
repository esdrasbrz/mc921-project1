# [MC921] Project 1 - Scanner and Parser
The goal of the first project is to implement a scanner, and a parser for the uC
language, specified by [uC BNF Grammar]. 

## Resources

Study the specification of uC grammar carefully. To complete this first project,
you will use the [PLY](http://www.dabeaz.com/ply/), a Python version of the
[lex/yacc](http://dinosaur.compilertools.net/) toolset with same functionality
but with a friendlier interface

## Set up the virtual enviroment
First and foremost, before running the project, one should setup the virtual
enviroment for python with this command ath the root of the project:

```basg
$ source bin/activate
```

## Install all requirements
After setting up the virtual enviroment, all required module should be installed
with this `pip` command:

```bash
$ pip3 install -r requirements.txt
```

## Testing a basic lex
To check if everything was done correctly, run this python script which will
test a very basic calculator lex:

```bash
$ python3 tester-lex.py
```

The output should be something like:

```
LexToken(NUMBER,3,2,8)
LexToken(PLUS,'+',2,10)
LexToken(NUMBER,4,2,12)
LexToken(TIMES,'*',2,14)
LexToken(NUMBER,10,2,16)
LexToken(PLUS,'+',3,23)
LexToken(MINUS,'-',3,25)
LexToken(NUMBER,20,3,26)
LexToken(TIMES,'*',3,29)
LexToken(NUMBER,2,3,30)
```

