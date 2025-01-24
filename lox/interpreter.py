from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Final, List, Optional, cast, override

from .environment import Environment
from .error_handler import BreakException, LoxRuntimeError, ReturnException
from .expr import (
    Assign,
    Binary,
    Call,
    Conditional,
    Expr,
    ExprVisitor,
    Get,
    Grouping,
    Literal,
    Logical,
    Set,
    Super,
    This,
    Unary,
    Variable,
)
from .lox_callable import (
    AbsCallable,
    ArrayCallable,
    CeilCallable,
    ClockCallable,
    CosCallable,
    ExpCallable,
    FloorCallable,
    LogCallable,
    LoxCallable,
    MaxCallable,
    MinCallable,
    RandomCallable,
    RandomRangeCallable,
    SinCallable,
    SqrtCallable,
    SumCallable,
    TanhCallable,
)
from .lox_class import LoxClass
from .lox_function import LoxFunction
from .lox_instance import LoxInstance
from .lox_trait import LoxTrait
from .stmt import (
    Block,
    Break,
    Class,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    StmtVisitor,
    Trait,
    Var,
    While,
)
from .tokens import Token, TokenType

if TYPE_CHECKING:
    from .lox_function import LoxFunction


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    """
    Interpreter for the Lox programming language.

    This class implements both `ExprVisitor` and `StmtVisitor` to evaluate expressions
    and execute statements within a given environment. It manages global and local
    environments, handles function calls, and integrates built-in functions.

    Attributes:
        globals (Environment): The global environment containing global variables and functions.
        _environment (Environment): The current environment, which may be nested within other environments.
        _locals (Dict[Expr, int]): A mapping of expressions to their resolved variable depth.
    """

    __slots__ = ("globals", "_environment", "_locals")

    def __init__(self) -> None:
        self.globals: Final[Environment] = Environment()
        self._environment: Environment = self.globals
        self._locals: Dict[Expr, int] = {}

        # Define built-in functions
        builtins = {
            "clock": ClockCallable(),
            "Array": ArrayCallable(),
            "max": MaxCallable(),
            "min": MinCallable(),
            "sum": SumCallable(),
            "randomrange": RandomRangeCallable(),
            "abs": AbsCallable(),
            "random": RandomCallable(),
            "exp": ExpCallable(),
            "log": LogCallable(),
            "sqrt": SqrtCallable(),
            "floor": FloorCallable(),
            "ceil": CeilCallable(),
            "sin": SinCallable(),
            "cos": CosCallable(),
            "tanh": TanhCallable(),
        }

        for name, func in builtins.items():
            self.globals.define(name, func)

    def _evaluate(self, expr: Optional[Expr]) -> Any:
        """
        Evaluate an expression.

        Args:
            expr (Optional[Expr]): The expression to evaluate.

        Returns:
            Any: The result of the evaluation.
        """
        if expr is None:
            return None
        return expr.accept(self)

    def _is_truthy(self, obj: Any) -> bool:
        """
        Determine if a value is truthy.

        Args:
            obj (Any): The object to evaluate.

        Returns:
            bool: True if the object is truthy, False otherwise.
        """
        return bool(obj)

    def _is_equal(self, a: Any, b: Any) -> bool:
        """
        Check if two values are equal.

        Args:
            a (Any): The first value.
            b (Any): The second value.

        Returns:
            bool: True if values are equal, False otherwise.
        """
        return a == b

    def _check_number_operand(self, operator: Token, operand: Any) -> None:
        """
        Ensure that the operand is a number.

        Args:
            operator (Token): The operator token.
            operand (Any): The operand to check.

        Raises:
            LoxRuntimeError: If the operand is not a number.
        """
        if not isinstance(operand, float):
            raise LoxRuntimeError(operator, "Operand must be a number.")

    def _check_number_operands(self, operator: Token, left: Any, right: Any) -> None:
        """
        Ensure that both operands are numbers.

        Args:
            operator (Token): The operator token.
            left (Any): The left operand.
            right (Any): The right operand.

        Raises:
            LoxRuntimeError: If either operand is not a number.
        """
        if not (isinstance(left, float) and isinstance(right, float)):
            raise LoxRuntimeError(operator, "Operands must be numbers.")

    def _stringify(self, obj: Any) -> str:
        """
        Convert an object to its string representation.

        Args:
            obj (Any): The object to stringify.

        Returns:
            str: The string representation.

        Raises:
            LoxRuntimeError: If the object is None.
        """
        if obj is None:
            raise LoxRuntimeError(
                Token(TokenType.NIL, "nil", None, 0),
                "Error: Variable access before initialization or assignment",
            )
        if isinstance(obj, float):
            return str(int(obj)) if obj % 1 == 0 else str(obj)
        return str(obj)

    def _execute(self, stmt: Stmt) -> None:
        """
        Execute a statement.

        Args:
            stmt (Stmt): The statement to execute.
        """
        stmt.accept(self)

    def _apply_trait(self, traits: List[Expr]) -> Dict[str, LoxFunction]:
        """
        Apply traits to the current environment.

        Args:
            traits (List[Expr]): A list of trait expressions.

        Returns:
            Dict[str, LoxFunction]: A dictionary of method names to LoxFunction instances.

        Raises:
            RuntimeError: If a trait is invalid or if there are conflicting methods.
        """
        methods: Dict[str, LoxFunction] = {}
        for trait_expr in traits:
            trait_obj: object = self._evaluate(trait_expr)
            if not isinstance(trait_obj, LoxTrait):
                no_trait: Token = cast(Variable, trait_expr).name
                raise RuntimeError(no_trait, f"{no_trait.lexeme} is not a trait.")
            trait: LoxTrait = cast(LoxTrait, trait_obj)
            for name, method in trait.methods.items():
                if name in methods:
                    raise RuntimeError(
                        Token(TokenType.IDENTIFIER, name, None, 0),
                        f"Duplicate method '{name}' found in traits.",
                    )
                methods[name] = method
        return methods

    def resolve(self, expr: Expr, depth: int) -> None:
        """
        Resolve the depth of a variable.

        Args:
            expr (Expr): The expression to resolve.
            depth (int): The depth at which the variable is found.
        """
        self._locals[expr] = depth

    def _execute_block(self, statements: List[Stmt], environment: Environment) -> None:
        """
        Execute a block of statements within a new environment.

        Args:
            statements (List[Stmt]): The statements to execute.
            environment (Environment): The new environment.
        """
        previous: Environment = self._environment
        try:
            self._environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous

    def interpret(self, statements: List[Stmt]) -> None:
        """
        Interpret a list of statements.

        Args:
            statements (List[Stmt]): The statements to interpret.
        """
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as e:
            print(e)

    @override
    def visit_literal_expr(self, expr: Literal) -> Any:
        """
        Visit a literal expression.

        Args:
            expr (Literal): The literal expression.

        Returns:
            Any: The value of the literal.
        """
        return expr.value

    @override
    def visit_grouping_expr(self, expr: Grouping) -> Any:
        """
        Visit a grouping expression.

        Args:
            expr (Grouping): The grouping expression.

        Returns:
            Any: The result of evaluating the grouped expression.
        """
        return self._evaluate(expr.expression)

    @override
    def visit_unary_expr(self, expr: Unary) -> Any:
        """
        Visit a unary expression.

        Args:
            expr (Unary): The unary expression.

        Returns:
            Any: The result of the unary operation.

        Raises:
            LoxRuntimeError: If operand type is incorrect.
        """
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                self._check_number_operand(expr.operator, right)
                return -right
            case TokenType.BANG:
                return not self._is_truthy(right)
        return None

    @override
    def visit_binary_expr(self, expr: Binary) -> Any:
        """
        Visit a binary expression.

        Args:
            expr (Binary): The binary expression.

        Returns:
            Any: The result of the binary operation.

        Raises:
            LoxRuntimeError: If operand types are incorrect or division by zero occurs.
        """
        left: Any = self._evaluate(expr.left)
        right: Any = self._evaluate(expr.right)

        match expr.operator.type:
            case TokenType.MINUS:
                self._check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.SLASH:
                self._check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise LoxRuntimeError(expr.operator, "Division by zero.")
                return left / right
            case TokenType.STAR:
                if isinstance(left, float) and isinstance(right, float):
                    return cast(float, left) * cast(float, right)
                elif isinstance(left, str) and isinstance(right, float):
                    return cast(str, left) * int(right)
                raise LoxRuntimeError(
                    expr.operator, "Operands must be numbers or a string and a number."
                )
            case TokenType.MODULO:
                self._check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise LoxRuntimeError(expr.operator, "Division by zero.")
                return left % right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                elif isinstance(left, str) and isinstance(right, float):
                    return left + self._stringify(right)
                elif isinstance(left, float) and isinstance(right, str):
                    return self._stringify(left) + right
                raise LoxRuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.GREATER:
                self._check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self._check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self._check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self._is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self._is_equal(left, right)
        return None

    @override
    def visit_variable_expr(self, expr: Variable) -> Any:
        """
        Visit a variable expression.

        Args:
            expr (Variable): The variable expression.

        Returns:
            Any: The value of the variable.
        """
        return self._lookup_variable(expr.name, expr)

    def _lookup_variable(self, name: Token, expr: Expr) -> Any:
        """
        Lookup the value of a variable.

        Args:
            name (Token): The token representing the variable's name.
            expr (Expr): The expression where the variable is used.

        Returns:
            Any: The value of the variable.

        Raises:
            RuntimeError: If the variable is undefined.
        """
        distance: int = self._locals.get(expr, -1)
        if distance != -1:
            return self._environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    @override
    def visit_assign_expr(self, expr: Assign) -> Any:
        """
        Visit an assignment expression.

        Args:
            expr (Assign): The assignment expression.

        Returns:
            Any: The assigned value.
        """
        value: Any = self._evaluate(expr.value)

        distance: int = self._locals.get(expr, -1)
        if distance != -1:
            self._environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)

        return value

    @override
    def visit_conditional_expr(self, expr: Conditional) -> Any:
        """
        Visit a conditional expression.

        Args:
            expr (Conditional): The conditional expression.

        Returns:
            Any: The result of the conditional expression.
        """
        if self._is_truthy(self._evaluate(expr.condition)):
            return self._evaluate(expr.then_branch)
        else:
            return self._evaluate(expr.else_branch)

    @override
    def visit_logical_expr(self, expr: Logical) -> Any:
        """
        Visit a logical expression.

        Args:
            expr (Logical): The logical expression.

        Returns:
            Any: The result of the logical operation.
        """
        left: Any = self._evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self._is_truthy(left):
                return left
        else:
            if not self._is_truthy(left):
                return left

        return self._evaluate(expr.right)

    @override
    def visit_set_expr(self, expr: Set) -> Any:
        """
        Visit a set expression.

        Args:
            expr (Set): The set expression.

        Returns:
            Any: The value that was set.

        Raises:
            LoxRuntimeError: If the object is not an instance.
        """
        obj: Any = self._evaluate(expr.object)

        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value: Any = self._evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    @override
    def visit_super_expr(self, expr: Super) -> Any:
        """
        Visit a super expression.

        Args:
            expr (Super): The super expression.

        Returns:
            Any: The bound method from the superclass.

        Raises:
            RuntimeError: If the method is undefined in the superclass.
        """
        distance: int = self._locals[expr]
        superclass: LoxClass = self._environment.get_at(distance, "super")
        obj: LoxInstance = self._environment.get_at(distance - 1, "this")
        method: Optional[LoxFunction] = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeError(
                expr.method, f"Undefined property '{expr.method.lexeme}.'"
            )
        return method.bind(obj)

    @override
    def visit_this_expr(self, expr: This) -> Any:
        """
        Visit a this expression.

        Args:
            expr (This): The this expression.

        Returns:
            Any: The current instance.
        """
        return self._lookup_variable(expr.keyword, expr)

    @override
    def visit_call_expr(self, expr: Call) -> Any:
        """
        Visit a call expression.

        Args:
            expr (Call): The call expression.

        Returns:
            Any: The result of the function or class call.

        Raises:
            LoxRuntimeError: If the callee is not callable or argument count mismatches.
        """
        callee: Any = self._evaluate(expr.callee)

        arguments: List[Any] = [self._evaluate(argument) for argument in expr.arguments]

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        function: LoxCallable = cast(LoxCallable, callee)

        if len(arguments) != function.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {function.arity()} arguments but got {len(arguments)}.",
            )

        return function.call(self, arguments)

    @override
    def visit_get_expr(self, expr: Get) -> Any:
        """
        Visit a get expression.

        Args:
            expr (Get): The get expression.

        Returns:
            Any: The value of the property.

        Raises:
            LoxRuntimeError: If the object does not have properties.
        """
        obj: Any = self._evaluate(expr.object)
        if isinstance(obj, LoxInstance):
            result = obj.get(expr.name)
            if isinstance(result, LoxFunction) and result.is_getter():
                return result.call(self, [])
            return result

        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    @override
    def visit_expression_stmt(self, stmt: Expression) -> None:
        """
        Visit an expression statement.

        Args:
            stmt (Expression): The expression statement.
        """
        self._evaluate(stmt.expression)

    @override
    def visit_print_stmt(self, stmt: Print) -> None:
        """
        Visit a print statement.

        Args:
            stmt (Print): The print statement.
        """
        value: Any = self._evaluate(stmt.expression)
        print(self._stringify(value))

    @override
    def visit_var_stmt(self, stmt: Var) -> None:
        """
        Visit a variable declaration statement.

        Args:
            stmt (Var): The variable declaration statement.
        """
        value: Any = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)

    @override
    def visit_block_stmt(self, stmt: Block) -> None:
        """
        Visit a block statement.

        Args:
            stmt (Block): The block statement.
        """
        self._execute_block(stmt.statements, Environment(self._environment))

    @override
    def visit_class_stmt(self, stmt: Class) -> None:
        """
        Visit a class declaration statement.

        Args:
            stmt (Class): The class declaration statement.

        Raises:
            RuntimeError: If the superclass is not a class.
        """
        superclass: Optional[LoxClass] = None
        if stmt.superclass:
            superclass_obj: Any = self._evaluate(stmt.superclass)
            if not isinstance(superclass_obj, LoxClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")
            superclass = superclass_obj

        self._environment.define(stmt.name.lexeme, None)

        if stmt.superclass:
            self._environment = Environment(self._environment)
            self._environment.define("super", superclass)

        class_methods: Dict[str, LoxFunction] = {
            method.name.lexeme: LoxFunction(method, self._environment, False)
            for method in stmt.class_methods
        }

        metaclass: LoxClass = LoxClass(
            None, f"{stmt.name.lexeme} metaclass", superclass, class_methods
        )

        methods: Dict[str, LoxFunction] = self._apply_trait(stmt.traits)

        methods.update(
            {
                method.name.lexeme: LoxFunction(
                    method, self._environment, method.name.lexeme == "init"
                )
                for method in stmt.methods
            }
        )

        klass: LoxClass = LoxClass(metaclass, stmt.name.lexeme, superclass, methods)

        if superclass:
            assert self._environment.enclosing is not None
            self._environment = self._environment.enclosing

        self._environment.assign(stmt.name, klass)

    @override
    def visit_if_stmt(self, stmt: If) -> None:
        """
        Visit an if statement.

        Args:
            stmt (If): The if statement.
        """
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self._execute(stmt.else_branch)

    @override
    def visit_while_stmt(self, stmt: While) -> None:
        """
        Visit a while statement.

        Args:
            stmt (While): The while statement.
        """
        while self._is_truthy(self._evaluate(stmt.condition)):
            try:
                self._execute(stmt.body)
            except BreakException:
                break

    @override
    def visit_break_stmt(self, stmt: Break) -> None:
        """
        Visit a break statement.

        Args:
            stmt (Break): The break statement.
        """
        raise BreakException()

    @override
    def visit_function_stmt(self, stmt: Function) -> None:
        """
        Visit a function declaration statement.

        Args:
            stmt (Function): The function declaration statement.
        """
        function: LoxFunction = LoxFunction(stmt, self._environment, False)
        self._environment.define(stmt.name.lexeme, function)

    @override
    def visit_return_stmt(self, stmt: Return) -> None:
        """
        Visit a return statement.

        Args:
            stmt (Return): The return statement.

        Raises:
            ReturnException: To unwind the call stack with the return value.
        """
        value: Any = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise ReturnException(value)

    @override
    def visit_trait_stmt(self, stmt: Trait) -> None:
        """
        Visit a trait declaration statement.

        Args:
            stmt (Trait): The trait declaration statement.

        Raises:
            RuntimeError: If a method name conflicts with existing trait methods.
        """
        self._environment.define(stmt.name.lexeme, None)

        methods: Dict[str, LoxFunction] = self._apply_trait(stmt.traits)

        for method in stmt.methods:
            if method.name.lexeme in methods:
                raise RuntimeError(
                    method.name,
                    f"A previous trait declares a method named '{method.name.lexeme}'.",
                )
            function: LoxFunction = LoxFunction(method, self._environment, False)
            methods[method.name.lexeme] = function

        trait: LoxTrait = LoxTrait(stmt.name, methods)

        self._environment.assign(stmt.name, trait)
