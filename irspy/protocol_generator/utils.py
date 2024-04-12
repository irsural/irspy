from typing import Any, Callable, Tuple, Dict


def handle_exceptions(*exceptions: type[Exception]) -> Callable[[Callable[..., None]], Callable[..., bool]]:
    def make_decorator(func: Callable[..., None]) -> Callable[..., bool]:
        def wrapper(*args: Any, **kwargs: Any) -> bool:
            try:
                func(*args, **kwargs)
                return True
            except (*exceptions, ) as ex:
                print('PROTOCOL GENERATION ERROR, EXCEPTION HANDLED:', str(ex))
                return False

        return wrapper

    return make_decorator
