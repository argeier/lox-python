# Python Lox Interpreter

A Python implementation of the Lox programming language, inspired by Bob Nystrom's [Crafting Interpreters](https://craftinginterpreters.com/). This project serves purely as a learning experience.

## About

Lox is a small, dynamically-typed language designed for educational purposes. This interpreter uses a tree-walk approach, as described in Part I of Bob Nystrom's "Crafting Interpreters," making it an excellent resource for anyone interested in language implementation.

### Learning Goals

- Grasp the fundamentals of interpreter and compiler design
- Implement key language features such as:
  - Lexical analysis and parsing
  - Abstract Syntax Trees (AST)
  - Recursive descent parsing
  - Variable scope and environment management
  - Control flow constructs
  - Functions, closures, and classes with inheritance

## Additional Features

Beyond the core implementation from "Crafting Interpreters," this interpreter includes:

- **Break Statements**: Allows exiting loops prematurely.
- **Multiline Comments**: Supports more readable and maintainable code.
- **Enhanced Error Detection**: Catches more runtime errors to aid debugging.
- **Improved Error Reporting**: Provides clearer and more informative error messages.
- **Static Analysis Enhancements**: Offers better compile-time checks for code correctness.
- **AST Printing and Visualization**: Helps visualize the structure of your code for easier understanding and debugging.

## Project Structure

lox/
├── interpreter.py    # Core interpreter implementation
├── parser.py        # Parser for Lox grammar
├── scanner.py       # Lexical analyzer
├── ast_printer.py   # Debug tool for AST visualization
├── resolver.py      # Static analysis and variable resolution
├── environment.py   # Scope and variable environment
└── error.py        # Error handling utilities

### Usage

- **Run a Lox file:**
    ```bash
    python lox.py path/to/your/script.lox
    ```

- **Run a Lox file with AST visualizations:**
    ```bash
    python lox.py path/to/your/script.lox -ast
    ```
    This will generate visualizations of the AST for each statement in the `assets/images/ast/` directory.

- **Start the REPL (interactive mode):**
    ```bash
    python lox.py
    ```

## Language Features

The interpreter supports all core Lox features, including:

- Arithmetic and logical expressions
- Variables and assignment
- Control flow (if, while, for)
- Functions and closures
- Classes with inheritance
- Standard library functions (print, clock)

### Example Lox Code

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

## Acknowledgments

- Bob Nystrom for the excellent ["Crafting Interpreters"](https://craftinginterpreters.com/) book
- The original Java implementation that this project is based on
- All the supplementary materials and errata from the Crafting Interpreters community

## License

This project is licensed under the MIT License - see the LICENSE file for details.