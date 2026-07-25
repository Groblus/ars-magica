"""Ars Magica reference-lab Python package.

Subpackages are intentionally not imported eagerly. The deterministic rules and
publishing helpers can run in constrained environments, while the domain models
require the core Pydantic dependency declared by the project package metadata.
"""

__all__ = ["__version__"]
__version__ = "0.1.0"
