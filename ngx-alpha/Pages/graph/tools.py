from langchain_core.tools import tool
from typing import Annotated, Tuple
from langgraph.prebuilt import InjectedState

import pandas as pd
import os
import sys
from io import StringIO

persistent_vars = {}

@tool
def complete_python_task(
    graph_state: Annotated[dict, InjectedState],
    thought: str,
    python_code: str
) -> Tuple[str, dict]:
    """
    Execute Python code for analysis and return output + updated state.
    """

    current_variables = graph_state.get("current_variables", {})

    # Load datasets
    for dataset in graph_state["input_data"]:
        if dataset.variable_name not in current_variables:
            current_variables[dataset.variable_name] = pd.read_csv(dataset.data_path)

    try:
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        exec_globals = {}
        exec_globals.update(persistent_vars)
        exec_globals.update(current_variables)

        exec(python_code, exec_globals)

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        # Persist variables across runs
        persistent_vars.update({
            k: v for k, v in exec_globals.items()
            if not k.startswith("__")
        })

        return output, {
            "intermediate_outputs": [{
                "thought": thought,
                "code": python_code,
                "output": output
            }],
            "current_variables": persistent_vars
        }

    except Exception as e:
        sys.stdout = old_stdout
        return str(e), {
            "intermediate_outputs": [{
                "thought": thought,
                "code": python_code,
                "output": str(e)
            }]
        }
