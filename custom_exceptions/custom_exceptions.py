from typing import Callable

def extraction_exception(inner_function: Callable):
    def inner_function(*args, **kwargs):
        try:
            inner_function(*args, **kwargs)
        except Exception as E:
            pass 
    
    return inner_function
