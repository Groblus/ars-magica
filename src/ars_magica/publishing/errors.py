"""Publishing-specific exceptions."""


class PublishingError(RuntimeError):
    """Base exception for publishing failures."""


class OptionalDependencyError(PublishingError):
    """Raised when a requested renderer is not installed."""


class TemplateNotFoundError(PublishingError):
    """Raised when a material template is unknown."""


class SourceReferenceError(PublishingError, ValueError):
    """Raised when publishing source references are ambiguous or malformed."""
