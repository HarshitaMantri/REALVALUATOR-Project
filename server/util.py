import pickle
import json
import numpy as np
import os
import sys

# Compatibility shim for pickles created with older scikit-learn
# Some older pickles reference sklearn.linear_model.base which was removed/renamed.
try:
    # try newer private module name
    from sklearn.linear_model import _base as _sklearn_linear_model_base
except Exception:
    try:
        # fallback for some older sklearn versions
        from sklearn.linear_model import base as _sklearn_linear_model_base
    except Exception:
        _sklearn_linear_model_base = None

if _sklearn_linear_model_base is not None:
    sys.modules['sklearn.linear_model.base'] = _sklearn_linear_model_base

# Fix for 'positive' parameter compatibility issue
# Patch LinearRegression to handle missing 'positive' attribute
try:
    from sklearn.linear_model import LinearRegression
    
    # Store original __setstate__ if it exists
    original_setstate = getattr(LinearRegression, '__setstate__', None)
    
    def patched_setstate(self, state):
        # Remove 'positive' from state if it exists and causes issues
        if 'positive' in state:
            # Check if current sklearn version supports 'positive'
            import sklearn
            sklearn_version = sklearn.__version__
            version_parts = [int(x) for x in sklearn_version.split('.')[:2]]
            # 'positive' was added in 0.24
            if version_parts[0] == 0 and version_parts[1] < 24:
                # Remove positive if version doesn't support it
                state.pop('positive', None)
            elif not hasattr(self, 'positive'):
                # If attribute doesn't exist, remove it from state
                state.pop('positive', None)
        
        # Call original setstate if it exists
        if original_setstate:
            original_setstate(self, state)
        else:
            # Fallback: set attributes manually
            self.__dict__.update(state)
    
    # Apply the patch
    LinearRegression.__setstate__ = patched_setstate
except Exception as e:
    print(f"Warning: Could not patch LinearRegression compatibility: {e}")

__locations = None
__data_columns = None
__model = None


def _resolve_artifacts_dir():
    """
    Determine where the artifacts live. Prefer an 'artifacts' folder in the
    project root but fall back to the legacy 'model' directory if needed.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    preferred = os.path.join(project_root, 'artifacts')
    legacy = os.path.join(project_root, 'model')

    if os.path.isdir(preferred):
        return preferred
    if os.path.isdir(legacy):
        return legacy

    raise FileNotFoundError(
        "Could not find an 'artifacts' or 'model' directory with the saved "
        "model files."
    )


def _resolve_artifact_file(preferred_names, prefix_hint=None):
    """
    Return the first existing file from preferred_names; if none are found
    and prefix_hint is provided, fall back to any file that starts with the
    hint. Raises FileNotFoundError otherwise.
    """
    for name in preferred_names:
        candidate = os.path.join(ARTIFACTS_DIR, name)
        if os.path.isfile(candidate):
            return candidate

    if prefix_hint:
        for entry in os.listdir(ARTIFACTS_DIR):
            if entry.startswith(prefix_hint):
                candidate = os.path.join(ARTIFACTS_DIR, entry)
                if os.path.isfile(candidate):
                    return candidate

    raise FileNotFoundError(
        f"Could not locate any of: {preferred_names} inside {ARTIFACTS_DIR}"
    )


ARTIFACTS_DIR = _resolve_artifacts_dir()
COLUMNS_PATH = _resolve_artifact_file(['columns.json'])
SAVED_MODEL_PATH = _resolve_artifact_file(
    ['banglore_home_prices_model(1).pickle',
     'banglore_home_prices_model (1).pickle'],
    prefix_hint='banglore_home_prices_model'
)

def get_estimated_price(location,sqft,bhk,bath):
    try:
        loc_index = __data_columns.index(location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(__data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    if loc_index>=0:
        x[loc_index] = 1

    # Fix for 'positive' attribute issue during prediction
    try:
        # Ensure positive attribute exists if needed
        if not hasattr(__model, 'positive'):
            setattr(__model, 'positive', False)
    except:
        pass
    
    try:
        return round(__model.predict([x])[0],2)
    except AttributeError as e:
        if 'positive' in str(e):
            # If positive attribute error, try to fix it and retry
            try:
                setattr(__model, 'positive', False)
                return round(__model.predict([x])[0],2)
            except:
                raise e
        else:
            raise e


def load_saved_artifacts():
    print("loading saved artifacts...start")
    global  __data_columns
    global __locations
    global __model  # if your code expects a module-level variable

    with open(COLUMNS_PATH, "r") as f:
        __data_columns = json.load(f)['data_columns']
        __locations = __data_columns[3:]  # first 3 columns are sqft, bath, bhk

    if __model is None:
        # Try multiple loading strategies
        loaded = False
        
        # Strategy 1: Try joblib (best for sklearn models)
        try:
            import joblib
            __model = joblib.load(SAVED_MODEL_PATH)
            print("Model loaded using joblib")
            loaded = True
        except (ImportError, Exception) as e:
            if 'ImportError' not in str(type(e)):
                print(f"Joblib load failed: {e}")
        
        # Strategy 2: Try regular pickle with error handling
        if not loaded:
            try:
                with open(SAVED_MODEL_PATH, 'rb') as f:
                    __model = pickle.load(f)
                print("Model loaded using pickle")
                loaded = True
            except AttributeError as e:
                if 'positive' in str(e):
                    # The error happened during unpickling due to 'positive' attribute
                    # Try to work around by monkey-patching before loading
                    print("Attempting to fix 'positive' attribute issue...")
                    try:
                        from sklearn.linear_model import LinearRegression
                        # Create a dummy instance to see what attributes it should have
                        dummy = LinearRegression()
                        # Now try loading again - sometimes the second attempt works
                        with open(SAVED_MODEL_PATH, 'rb') as f:
                            __model = pickle.load(f)
                        # Force set positive if missing
                        if not hasattr(__model, 'positive'):
                            setattr(__model, 'positive', getattr(dummy, 'positive', False))
                        print("Model loaded with workaround")
                        loaded = True
                    except Exception as e2:
                        print(f"Workaround failed: {e2}")
                        raise e
                else:
                    raise e
            except Exception as e:
                if not loaded:
                    raise e
        
        # Ensure positive attribute exists
        if loaded and not hasattr(__model, 'positive'):
            try:
                setattr(__model, 'positive', False)
            except:
                pass
    
    print("loading saved artifacts...done")

def get_location_names():
    return __locations

def get_data_columns():
    return __data_columns

if __name__ == '__main__':
    load_saved_artifacts()
    print(get_location_names())
    print(get_estimated_price('1st Phase JP Nagar',1000, 3, 3))
    print(get_estimated_price('1st Phase JP Nagar', 1000, 2, 2))
    print(get_estimated_price('Kalhalli', 1000, 2, 2)) # other location
    print(get_estimated_price('Ejipura', 1000, 2, 2))  # other location