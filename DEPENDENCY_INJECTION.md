# Dependency Injection & Inversion of Control

This document explains how dependency injection (DI) and inversion of control (IoC) are implemented in this project.

## Overview

The project implements **Dependency Injection** following the **Dependency Inversion Principle** (the "D" in SOLID). This ensures:

- **Loose coupling** between layers
- **Easy testing** with mock dependencies
- **Flexibility** to swap implementations
- **Better maintainability** and code organization

## Architecture Layers

The project follows Clean Architecture with proper dependency flow:

```
Presentation Layer (API/Controllers)
         ↓ depends on
Application Layer (Services/Use Cases)
         ↓ depends on
Domain Layer (Entities/Interfaces)
         ↑ implemented by
Infrastructure Layer (Repositories/External Services)
```

**Key Principle**: Inner layers define interfaces, outer layers implement them. Dependencies always point inward.

## Implementation

### 1. FastAPI's Built-in Dependency Injection

FastAPI provides a powerful DI system through `Depends()`:

```python
from fastapi import Depends
from typing import Annotated

# Define a dependency
def get_database():
    db = Database()
    try:
        yield db
    finally:
        db.close()

# Use in route handler
@app.get("/users")
async def get_users(db: Annotated[Database, Depends(get_database)]):
    return db.query_users()
```

### 2. Custom IoC Container

For more complex scenarios, we provide a simple IoC container:

```python
from src.shared.infra.container import container

# Register dependencies
container.register(IRepository, ConcreteRepository)
container.register(IService, ConcreteService, singleton=True)

# Resolve dependencies
repo = container.resolve(IRepository)
```

## Project Structure

### Dependencies Module

Each module has its own `dependencies.py` file:

```
src/
├── shared/
│   └── infra/
│       ├── dependencies.py      # Shared dependencies
│       └── container.py          # IoC container
├── account/
│   └── infra/
│       └── dependencies.py      # Account module dependencies
└── notification/
    └── infra/
        └── dependencies.py      # Notification module dependencies
```

## Usage Examples

### Example 1: Basic Dependency Injection

**Before (Anti-pattern):**
```python
# ❌ Service instantiated at module level - tight coupling
account_service = AccountService()

@router.post("/account")
def create_account(account_in: AccountCreate):
    return account_service.create(account_in)
```

**After (Proper DI):**
```python
# ✅ Service injected per-request - loose coupling
from src.account.infra.dependencies import AccountServiceDep

@router.post("/account")
async def create_account(
    service: AccountServiceDep,
    account_in: AccountCreate,
):
    return await service.create(account_in)
```

### Example 2: Service with Repository Injection

**Service Definition:**
```python
class AccountService:
    """Service with injected repository."""
    
    def __init__(self, repository: AccountRepository):
        """Constructor injection - repository is injected."""
        self.repository = repository
    
    async def create(self, data: AccountCreate):
        return await self.repository.create(data)
```

**Dependency Provider:**
```python
# src/account/infra/dependencies.py

def get_account_repository() -> AccountRepository:
    """Provide repository instance."""
    return AccountRepository(Account)

def get_account_service(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> AccountService:
    """Provide service with injected repository."""
    return AccountService(repository)

# Type alias for cleaner annotations
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
```

**Usage in Route:**
```python
@router.post("/account")
async def create_account(
    db: DatabaseSession,
    service: AccountServiceDep,  # Service with repository injected
    account_in: AccountCreate,
):
    return await service.create(db, obj_in=account_in)
```

### Example 3: Multiple Dependencies

```python
@router.post("/account/transfer")
async def transfer_money(
    db: DatabaseSession,
    account_service: AccountServiceDep,
    notification_service: NotificationServiceDep,
    audit_logger: AuditLoggerDep,
    transfer_data: TransferData,
):
    # All dependencies are injected
    account = await account_service.transfer(db, transfer_data)
    await notification_service.send(account.email, "Transfer completed")
    await audit_logger.log("transfer", account.id)
    return account
```

### Example 4: Testing with Mocks

```python
# test_account.py
from unittest.mock import Mock
from fastapi.testclient import TestClient

def test_create_account():
    # Create mock repository
    mock_repo = Mock(spec=AccountRepository)
    mock_repo.create.return_value = Account(id=1, email="test@example.com")
    
    # Override dependency
    app.dependency_overrides[get_account_repository] = lambda: mock_repo
    
    # Test endpoint
    client = TestClient(app)
    response = client.post("/account", json={"email": "test@example.com"})
    
    assert response.status_code == 200
    mock_repo.create.assert_called_once()
```

## Dependency Injection Patterns

### 1. Constructor Injection (Recommended)

```python
class AccountService:
    def __init__(self, repository: AccountRepository):
        self.repository = repository
```

**Pros:**
- Dependencies are explicit and required
- Immutable after construction
- Easy to test

### 2. Property Injection (Avoid)

```python
class AccountService:
    repository: AccountRepository = None
    
    def set_repository(self, repo: AccountRepository):
        self.repository = repo
```

**Cons:**
- Dependencies can be changed after construction
- Not clear what's required
- Harder to test

### 3. Method Injection

```python
class AccountService:
    def create(self, db: Session, repository: AccountRepository):
        return repository.create(db)
```

**Use case:**
- When dependency is only needed for specific methods
- When dependency varies per method call

## Type Aliases for Clean Code

Use type aliases to make dependency annotations cleaner:

```python
# Define once
from typing import Annotated
from fastapi import Depends

DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]

# Use everywhere
@router.post("/account")
async def create_account(
    db: DatabaseSession,  # Clean!
    service: AccountServiceDep,  # Clean!
):
    pass
```

## Dependency Lifecycle

### Per-Request (Default)

```python
def get_account_service() -> AccountService:
    """New instance per request."""
    return AccountService(AccountRepository())
```

### Singleton

```python
# Using container
container.register(CacheService, RedisCacheService, singleton=True)

# Or with FastAPI
@lru_cache()
def get_cache_service() -> CacheService:
    """Single instance shared across requests."""
    return RedisCacheService()
```

### Scoped (Database Session)

```python
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Session scoped to request lifecycle."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Best Practices

### 1. Depend on Abstractions, Not Concretions

```python
# ✅ Good - depends on interface
class AccountService:
    def __init__(self, repository: IAccountRepository):
        self.repository = repository

# ❌ Bad - depends on concrete class
class AccountService:
    def __init__(self):
        self.repository = PostgresAccountRepository()
```

### 2. Use Type Aliases

```python
# ✅ Good - clean and reusable
AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]

@router.post("/account")
async def create(service: AccountServiceDep):
    pass

# ❌ Bad - verbose and repetitive
@router.post("/account")
async def create(service: Annotated[AccountService, Depends(get_account_service)]):
    pass
```

### 3. Keep Dependencies Explicit

```python
# ✅ Good - all dependencies are visible
def get_account_service(
    repository: AccountRepositoryDep,
    cache: CacheDep,
    logger: LoggerDep,
) -> AccountService:
    return AccountService(repository, cache, logger)

# ❌ Bad - hidden dependencies
def get_account_service() -> AccountService:
    repo = AccountRepository()
    cache = RedisCache()
    logger = Logger()
    return AccountService(repo, cache, logger)
```

### 4. Don't Create Dependencies at Module Level

```python
# ❌ Bad - created at import time
account_service = AccountService()

@router.post("/account")
def create(account_in: AccountCreate):
    return account_service.create(account_in)

# ✅ Good - created per request
@router.post("/account")
async def create(
    service: AccountServiceDep,
    account_in: AccountCreate,
):
    return await service.create(account_in)
```

### 5. Use Dependency Overrides for Testing

```python
# test_account.py
def test_create_account():
    # Override real dependency with mock
    app.dependency_overrides[get_account_service] = lambda: MockAccountService()
    
    client = TestClient(app)
    response = client.post("/account", json={...})
    
    assert response.status_code == 200
    
    # Clean up
    app.dependency_overrides.clear()
```

## Common Patterns

### Pattern 1: Service Layer with Repository

```python
# Repository (Infrastructure Layer)
class AccountRepository:
    def __init__(self, model: type[Account]):
        self.model = model

# Service (Application Layer)
class AccountService:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

# Dependencies (Infrastructure Layer)
def get_account_repository() -> AccountRepository:
    return AccountRepository(Account)

def get_account_service(
    repository: Annotated[AccountRepository, Depends(get_account_repository)],
) -> AccountService:
    return AccountService(repository)

# Route (Presentation Layer)
@router.post("/account")
async def create_account(
    db: DatabaseSession,
    service: AccountServiceDep,
    account_in: AccountCreate,
):
    return await service.create(db, obj_in=account_in)
```

### Pattern 2: Composite Services

```python
class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        payment_service: PaymentService,
        notification_service: NotificationService,
    ):
        self.order_repo = order_repo
        self.payment_service = payment_service
        self.notification_service = notification_service

def get_order_service(
    order_repo: OrderRepositoryDep,
    payment_service: PaymentServiceDep,
    notification_service: NotificationServiceDep,
) -> OrderService:
    return OrderService(order_repo, payment_service, notification_service)
```

### Pattern 3: Factory Pattern

```python
class RepositoryFactory:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def create_account_repository(self) -> AccountRepository:
        return AccountRepository(Account, self.db)
    
    def create_order_repository(self) -> OrderRepository:
        return OrderRepository(Order, self.db)

def get_repository_factory(db: DatabaseSession) -> RepositoryFactory:
    return RepositoryFactory(db)
```

## Troubleshooting

### Issue: Circular Dependencies

**Problem:**
```python
# service.py
from repository import Repository

class Service:
    def __init__(self, repo: Repository):
        self.repo = repo

# repository.py
from service import Service  # Circular!

class Repository:
    def __init__(self, service: Service):
        self.service = service
```

**Solution:**
Use interfaces or forward references:
```python
# interfaces.py
from abc import ABC

class IRepository(ABC):
    pass

class IService(ABC):
    pass

# service.py
from interfaces import IRepository

class Service(IService):
    def __init__(self, repo: IRepository):
        self.repo = repo
```

### Issue: Dependency Not Found

**Problem:**
```
KeyError: Service AccountService not registered
```

**Solution:**
Ensure dependency is registered or provider function is defined:
```python
# Make sure this exists
def get_account_service() -> AccountService:
    return AccountService(AccountRepository())
```

## Summary

This project implements proper dependency injection following these principles:

1. ✅ **Dependency Inversion**: Depend on abstractions, not concretions
2. ✅ **Constructor Injection**: Dependencies injected through constructors
3. ✅ **FastAPI Depends**: Using FastAPI's built-in DI system
4. ✅ **Type Safety**: Full type hints for all dependencies
5. ✅ **Testability**: Easy to mock and test with dependency overrides
6. ✅ **Lifecycle Management**: Proper scoping (per-request, singleton, scoped)
7. ✅ **Clean Code**: Type aliases for cleaner annotations

## Further Reading

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

