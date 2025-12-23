"""Dependency Injection Container.

This module provides a simple but effective IoC container for managing
dependencies throughout the application. It follows the Dependency Inversion
Principle from SOLID.

Benefits:
- Loose coupling between layers
- Easy testing with mock dependencies
- Centralized dependency configuration
- Lifecycle management
"""
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class Container:
    """Simple dependency injection container.
    
    This container manages the creation and lifecycle of dependencies,
    allowing for easy swapping of implementations (e.g., for testing).
    
    Example:
        >>> container = Container()
        >>> container.register(IRepository, ConcreteRepository)
        >>> repo = container.resolve(IRepository)
    """
    
    def __init__(self) -> None:
        """Initialize the container."""
        self._services: dict[type, Callable[..., Any]] = {}
        self._singletons: dict[type, Any] = {}
    
    def register(
        self,
        interface: type[T],
        implementation: type[T] | Callable[..., T],
        singleton: bool = False,
    ) -> None:
        """Register a service in the container.
        
        Args:
            interface: The interface or abstract class.
            implementation: The concrete implementation or factory function.
            singleton: If True, only one instance will be created.
        """
        self._services[interface] = implementation
        if singleton:
            self._singletons[interface] = None
    
    def register_instance(self, interface: type[T], instance: T) -> None:
        """Register an existing instance as a singleton.
        
        Args:
            interface: The interface or abstract class.
            instance: The instance to register.
        """
        self._services[interface] = lambda: instance
        self._singletons[interface] = instance
    
    def resolve(self, interface: type[T], **kwargs: Any) -> T:
        """Resolve a dependency from the container.
        
        Args:
            interface: The interface to resolve.
            **kwargs: Additional arguments to pass to the constructor.
            
        Returns:
            An instance of the requested type.
            
        Raises:
            KeyError: If the interface is not registered.
        """
        if interface not in self._services:
            raise KeyError(f"Service {interface.__name__} not registered")
        
        # Return singleton if already created
        if interface in self._singletons and self._singletons[interface] is not None:
            return self._singletons[interface]
        
        # Create new instance
        implementation = self._services[interface]
        
        if callable(implementation):
            instance = implementation(**kwargs)
        else:
            instance = implementation
        
        # Store singleton
        if interface in self._singletons:
            self._singletons[interface] = instance
        
        return instance
    
    def clear(self) -> None:
        """Clear all registrations (useful for testing)."""
        self._services.clear()
        self._singletons.clear()


# Global container instance
container = Container()


def get_container() -> Container:
    """Get the global container instance.
    
    Returns:
        The global container.
    """
    return container

