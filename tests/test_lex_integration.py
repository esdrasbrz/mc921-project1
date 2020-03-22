lex_identifier_test = r'''
_int = 333
float1 = 444.4
string = "Hello World \n"
// test inline comment
/* test block comment */
/* "This is a string inside a block comment" */
'''

lex_reserved_test = r'''
if void else char for break
while float assert int
print read return
'''

lex_test_all = r'''
// test inline comment
if void else char for break

/* test block comment */
/* "This is a string inside a block comment" */
_int = 333
float1 = 444.4
string = "Hello World\n"

while float assert int
print read return
'''

lex_example_1 = r'''
int main () {
    int v[] = {1, 2, 3, 4, 5};
    int k = 3;
    int p = v[k];
    assert p == 4;
    return;
}
'''

lex_example_2 = r'''
int main () {
    float f = 1.0;
    char s[] = "xpto";
    print("este é um teste:", s);
    print(f);
    return 0;
}
'''

lex_example_3 = r'''
int n = 3;

int doubleMe (int x) {
    return x * x;
}

void main () {
    int v = n;
    v = doubleMe (v);
    assert v == n * n;
    return 0;
}
'''

lex_example_4 = r'''
int main () {
    int i, j;
    i = 1;
    j = 2;
    for (int k=1; k<10; k++)
        i += j * k;
    assert i == 91;
    return 0;
}
'''

lex_example_5 = r'''
int main() {
    int var[] = {100, 200, 300};
    int *ptr;
    ptr = var;
    for(int i = 0; i < MAX; i++) {
        assert var[i] == *ptr;
        ptr++;
    }
    return 0;
}
'''

lex_example_6 = r'''
int main() {
    int h, b;
    float area;
    read(h);
    read(b);
    /*
        Formula for the area of the triangle = (height x base)/2
        Also, typecasting denominator from int to float
    */
    area = (h*b)/(float)2;
    print("The area of the triangle is: ", area);
    return 0;
}
'''

def test_lex_identifiers(lex):
    """
    Integration test for the lex, tests identifiers
    :return:
    """
    lex.input(lex_identifier_test)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
    pass

def test_lex_reserved(lex):
    """
    Integration test for the lex, tests reserved keywords
    :return:
    """
    lex.input(lex_reserved_test)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
    pass

def test_lex_all(lex):
    """
    Integration test for the lexer, test all possible cases
    :return:
    """
    lex.input(lex_test_all)

    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
    pass

def test_example_6(lex):
    """
    Integration test for the lexer, test all possible cases
    :return:
    """
    lex.input(lex_example_6)
    while True:
        tok = lex.token()
        if not tok:
            break  # No more input
    pass
