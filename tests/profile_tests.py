import cProfile
import os
import pstats
import io
from functools import wraps

def profile_test(func):
    @wraps(func)  # This preserves the original function's signature
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()

            # Create the profiling folder if it doesn't exist
            profiling_folder = "profiling_data"
            os.makedirs(profiling_folder, exist_ok=True)

            # Save the .prof file in the folder
            file_name = os.path.join(profiling_folder, f"{func.__name__}.prof")
            # Collect and print profiling stats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats(pstats.SortKey.TIME)
            profiler.dump_stats(file_name)
            print(f"Profiling data saved to {file_name}")

        return result
    return wrapper
# use snakeviz <function_name>.prof to see the profiling
