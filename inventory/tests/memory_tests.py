from memory_profiler import memory_usage
from functools import wraps

def log_memory(output_file="all_memory_usage.log"):
    """
    A decorator to log memory usage of test functions to a single file.

    Args:
        output_file (str): The file where memory usage logs will be written.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Profile the memory usage of the function
            mem_usage, result = memory_usage((func, args, kwargs), retval=True, interval=0.1)
            max_mem = max(mem_usage)

            # Append memory profiling results to the file
            with open(output_file, "a") as log:
                log.write(f"{func.__name__}: {max_mem:.2f} MB\n")
            
            return result
        return wrapper
    return decorator