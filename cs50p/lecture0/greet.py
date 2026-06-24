# CS50P L0 — defining a function with a default parameter.
# Tweak: I call greet() twice — once via main() with user input,
# once with no argument so the default ("World") prints right after.

def main():
    name = input("What's your name? ")
    greet(name)          

def greet(name="World"):
    print("Hello,", name)

main()  
greet() 