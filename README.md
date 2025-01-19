# Python Lox Interpreter

This is a Python implementation of the Lox programming language, based on the Java code from Bob Nystrom's excellent book ["Crafting Interpreters"](https://craftinginterpreters.com/). This project was created as a learning exercise to understand how interpreters and compilers work by translating the original Java implementation into Python.

## About

Lox is a small dynamically-typed programming language created for educational purposes. This interpreter implements the tree-walk interpreter described in Part I of the book ("A Tree-Walk Interpreter").

### Learning Goals

- Understanding interpreter and compiler design principles
- Practicing language implementation concepts like:
  - Lexical analysis (scanning)
  - Parsing
  - Abstract syntax trees
  - Recursive descent parsing
  - Runtime representation
  - Static analysis
  - Scope
  - Resolving and binding
  - Control flow
  - Functions and closures
  - Classes and inheritance

## Additional Features

Beyond the base implementation from the book, this version includes solutions to the challenges presented throughout the chapters:

- Break statements for loops
- Multiline comments support
- Additional runtime error detection
- Improved error reporting
- Static analysis enhancements
- AstPrinting and Visualization

## Getting Started

### Prerequisites

- Python 3.8 or higher

### Installation

```bash
git clone https://github.com/yourusername/lox-interpreter.git
cd lox-interpreter
```

### Usage

Run a Lox file:
```bash
python lox.py path/to/your/script.lox
```

Start REPL (interactive mode):
```bash
python lox.py
```

## Language Features

The interpreter supports all core Lox features including:

- Arithmetic and logical expressions
- Variables and assignment
- Control flow (if, while, for)
- Functions and closures
- Classes with inheritance
- Standard library functions (print, clock)

Example Lox code:
```lox
// Classes and inheritance
class Animal {
  speak() {
    print "Animal makes a sound";
  }
}

class Dog < Animal {
  speak() {
    print "Dog says woof!";
  }
}

var dog = Dog();
dog.speak(); // Prints: Dog says woof!

// Functions and closures
fun makeCounter() {
  var i = 0;
  fun count() {
    i = i + 1;
    print i;
  }
  return count;
}

var counter = makeCounter();
counter(); // Prints: 1
counter(); // Prints: 2
```

## Project Structure

```
lox/
├── interpreter.py    # Core interpreter implementation
├── parser.py        # Parser for Lox grammar
├── scanner.py       # Lexical analyzer
├── ast_printer.py   # Debug tool for AST visualization
├── resolver.py      # Static analysis and variable resolution
├── environment.py   # Scope and variable environment
└── error.py        # Error handling utilities
```

## Limitations

This is an educational project and has several limitations:

- It's a tree-walk interpreter, so it's not optimized for performance
- Error recovery is basic
- No standard library beyond essential functions
- Not intended for production use

## Acknowledgments

- Bob Nystrom for the excellent ["Crafting Interpreters"](https://craftinginterpreters.com/) book
- The original Java implementation that this project is based on
- All the supplementary materials and errata from the Crafting Interpreters community

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This interpreter is a learning tool created by following "Crafting Interpreters" and translating its Java code to Python. It is not intended for production use and exists primarily as an educational exercise in understanding interpreter design and implementation.