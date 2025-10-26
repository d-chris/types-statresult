import ast
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
    - Removes unnecessary empty lines
    - Changes definition to 'class stat_result(typing.Protocol)'
    """

    # Parse the code into an AST
    tree = ast.parse(code)
    class_node = None

    # Find the 'stat_result' class definition
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "stat_result":
            class_node = node
            break

    if class_node is None:
        raise ValueError("Class 'stat_result' not found in code")

    # Remove unwanted decorators
    new_decorators = []
    for decorator in class_node.decorator_list:
        # Extract decorator name
        if isinstance(decorator, ast.Name):
            name = decorator.id
        elif isinstance(decorator, ast.Attribute):
            name = decorator.attr
        else:
            name = None

        # Keep only if not @final or @deprecated
        if name not in {"final", "deprecated"}:
            new_decorators.append(decorator)

    class_node.decorator_list = new_decorators

    # Helper function to remove @deprecated decorator from a node
    def remove_deprecated_decorator(node):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return
        new_decorators = []
        for decorator in node.decorator_list:
            is_deprecated = False
            if isinstance(decorator, ast.Name) and decorator.id == "deprecated":
                is_deprecated = True
            elif (
                isinstance(decorator, ast.Attribute) and decorator.attr == "deprecated"
            ):
                is_deprecated = True
            elif isinstance(decorator, ast.Call):
                func = decorator.func
                if isinstance(func, ast.Name) and func.id == "deprecated":
                    is_deprecated = True
                elif isinstance(func, ast.Attribute) and func.attr == "deprecated":
                    is_deprecated = True

            if not is_deprecated:
                new_decorators.append(decorator)

        node.decorator_list = new_decorators

    # Helper function to process body items recursively
    def process_body(body_items):
        new_items = []
        for item in body_items:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                remove_deprecated_decorator(item)
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

    # Remove @deprecated from all methods/properties and replace __match_args__
    class_node.body = process_body(class_node.body)

    # Change base classes to typing.Protocol
    class_node.bases = [
        ast.Attribute(
            value=ast.Name(id="typing", ctx=ast.Load()), attr="Protocol", ctx=ast.Load()
        )
    ]

    # Generate the code for the class
    generated_code = astor.to_source(class_node)

    # Format with black
    full_code = "import sys\nimport typing\n\n" + generated_code.strip()

    return black.format_str(full_code, mode=black.Mode())


if __name__ == "__main__":
    stub = get_code()
    code = get_statresult(stub)
    Path("ostypes.py").write_text(code + "\n", encoding="utf-8")
