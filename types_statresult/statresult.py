import ast
import typing as t
from importlib.util import find_spec
from pathlib import Path

import astor
import black


def get_code() -> str:
    """Get the code from the mypy.typeshed.stdlib.os module stub file."""

    stub = "mypy.typeshed.stdlib.os"

    spec = find_spec(stub)

    try:
        origin = spec.submodule_search_locations[0]  # type: ignore
    except Exception:
        raise FileNotFoundError(f"Could not find {stub=!s}")

    file = Path(origin).joinpath("__init__.pyi").resolve(True)

    return file.read_text(encoding="utf-8")


def get_statresult(code: str) -> str:
    """
    Extracts and refactors the 'stat_result' class from a Python file.
    - Removes decorators @final and @deprecated
    - Replaces __match_args__ with pass
    - Changes definition to 'class stat_result(typing.Protocol)'
    """

    # Parse the code into an AST
    tree = ast.parse(code)

    # Find the 'stat_result' class definition
    class_node = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "stat_result"
        ),
        None,
    )

    if class_node is None:
        raise ValueError("Class 'stat_result' not found in code")

    # Helper function to check if decorator is deprecated
    def is_deprecated(decorator):
        if isinstance(decorator, ast.Name):
            return decorator.id == "deprecated"
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr == "deprecated"
        elif isinstance(decorator, ast.Call):
            func = decorator.func
            if isinstance(func, ast.Name):
                return func.id == "deprecated"
            elif isinstance(func, ast.Attribute):
                return func.attr == "deprecated"
        return False

    # Remove unwanted class decorators (@final, @deprecated)
    class_node.decorator_list = [
        dec
        for dec in class_node.decorator_list
        if not (
            (isinstance(dec, ast.Name) and dec.id in {"final", "deprecated"})
            or (isinstance(dec, ast.Attribute) and dec.attr in {"final", "deprecated"})
        )
    ]

    # Helper function to process body items recursively
    def process_body(body_items):
        new_items = []
        for item in body_items:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Remove @deprecated decorators from methods/properties
                item.decorator_list = [
                    dec for dec in item.decorator_list if not is_deprecated(dec)
                ]
                new_items.append(item)
            elif isinstance(item, ast.If):
                # Recursively process if blocks
                item.body = process_body(item.body)
                item.orelse = process_body(item.orelse)
                new_items.append(item)
            elif isinstance(item, ast.AnnAssign):
                # Replace __match_args__ assignment with pass
                if (
                    isinstance(item.target, ast.Name)
                    and item.target.id == "__match_args__"
                ):
                    new_items.append(ast.Pass())
                else:
                    new_items.append(item)
            else:
                new_items.append(item)
        return new_items

    # Process class body
    class_node.body = process_body(class_node.body)

    # Change base classes to typing.Protocol
    class_node.bases = [
        ast.Attribute(
            value=ast.Name(id="typing", ctx=ast.Load()), attr="Protocol", ctx=ast.Load()
        )
    ]

    # Generate the code for the class using astor
    generated_code = astor.to_source(class_node)

    # Format with black
    return generated_code.strip()


def refactor_statresult(refactor: t.Callable[[str, str], str]) -> str:
    """
    Parse code and refactor type hints for properties in the stat_result class.

    Args:
        refactor: Callback function that takes (name, type) and returns new type

    Returns:
        Refactored code with updated type hints
    """
    tree = ast.parse(
        get_statresult(
            get_code(),
        )
    )

    # Find the stat_result class
    stat_result_class = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "stat_result"
        ),
    )

    # Helper function to refactor properties recursively
    def refactor_properties(body_items):
        for item in body_items:
            if isinstance(item, ast.FunctionDef):
                # Check if it's a property (has @property decorator)
                is_property = any(
                    (isinstance(dec, ast.Name) and dec.id == "property")
                    or (isinstance(dec, ast.Attribute) and dec.attr == "property")
                    for dec in item.decorator_list
                )

                if is_property and item.returns:
                    # Get the return type annotation
                    if isinstance(item.returns, ast.Name):
                        old_type = item.returns.id
                        new_type = refactor(item.name, old_type)
                        item.returns = ast.Name(id=new_type, ctx=ast.Load())
                    elif isinstance(item.returns, ast.Attribute):
                        old_type = item.returns.attr
                        new_type = refactor(item.name, old_type)
                        item.returns = ast.Name(id=new_type, ctx=ast.Load())

            elif isinstance(item, ast.If):
                # Recursively process if blocks
                refactor_properties(item.body)
                refactor_properties(item.orelse)

    if callable(refactor):
        # Refactor properties in the stat_result class
        refactor_properties(stat_result_class.body)

    # Use astor for consistent code generation
    return astor.to_source(tree).strip()


def black_fmt(code: str, **kwargs) -> str:
    """Format code using black."""
    return black.format_str(code, mode=black.Mode(**kwargs))
