# Maps tool names to function handlers
from .summary import show_summary
from .scatter import plot_scatter
from .line import plot_line
from .bar import plot_bar
from .histogram import plot_histogram
from .correlation import plot_correlation
from .pie import plot_pie

TOOL_FUNCTIONS = {
    "summary": show_summary,
    "scatter": plot_scatter,
    "line": plot_line,
    "bar": plot_bar,
    "histogram": plot_histogram,
    "correlation": plot_correlation,
    "pie": plot_pie,
}
print("entered tools init")