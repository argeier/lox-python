# Python Lox Interpreter

This is a Python implementation of the Lox programming language, based on Bob Nystrom's book [Crafting Interpreters](https://craftinginterpreters.com/). The project serves as a learning exercise to understand interpreter design and implementation.

## About

This implementation follows the tree-walk interpreter design from the book, but translates the original Java code to Python while adding some extra features:

- AST visualization using Graphviz (generates PNG images of the abstract syntax tree)
- Support for traits (similar to Rust traits or Java interfaces)
- Additional built-in math functions (sin, cos, exp, log, etc.)
- Ternary operator support
- Array data structure with get/set operations
- Better REPL with multi-line input support
- Extended error handling and reporting

## Requirements

- Python 3.12 or higher (required for @override decorator)
- pygraphviz (for AST visualization)

## Installation

```bash
pip install e .
```

## Usage

Run the REPL:
```bash
python -m lox
```

Run a Lox file:
```bash
python -m lox path/to/your/script.lox
```

Generate AST visualizations:
```bash
python -m lox -ast path/to/your/script.lox
```

The AST visualizations will be generated as PNG files in the `assets/images/ast` directory. Each statement in your Lox program will create a corresponding visualization.

## Examples

The repository includes a variety of example programs showcasing Lox's capabilities like:

- `examples/nn3x3.lox`: A neural network implementation for X pattern recognition in a 3x3 grid
- `examples/nn5x5.lox`: A more advanced neural network for digit recognition using a 5x5 grid
- `examples/builtins.lox`: Demonstrates built-in functions and operations
- `examples/doublylinkedlist.lox`: Implementation of a doubly linked list data structure
- `examples/nnXOR.lox`: Neural network implementation for XOR problem
- `examples/rule110.lox`: Implementation of Rule 110 cellular automaton
- `examples/singlylinkedlist.lox`: Implementation of a singly linked list

## Language Features

- Standard control flow (if, while, for)
- Functions and closures
- Classes with inheritance
- Traits for interface-like behavior
- Dynamic typing
- Built-in array type and mathematical functions
- String operations

## Acknowledgments

This project is a learning implementation based on Bob Nystrom's "Crafting Interpreters". The original book and Java implementation can be found at https://craftinginterpreters.com/.

## License

Feel free to use this code for learning purposes. The original Lox language design and implementation concepts are from "Crafting Interpreters" by Bob Nystrom.