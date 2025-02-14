from typing import Callable

def extraction_exception(inner_function: Callable):
    def wrapper_function(*args, **kwargs):
        try:
            inner_function(*args, **kwargs)
        except Exception as E:
            pass 
    
    return wrapper_function

def database_upload_exception(inner_function: Callable):
    def wrapper_function(*args, **kwargs):
        try: 
            inner_function(*args, **kwargs)
        except Exception as E: 
            pass 

    return wrapper_function
