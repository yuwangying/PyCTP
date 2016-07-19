def fun_log(fn):
    def wrapper(*args, **kwargs):
        print("Before Calling %s" %fn.__name__)
        retval = fn(*args, **kwargs)
        # print("After Calling %s" %fn.__name__)
        return retval
    return wrapper

def fun_log_message(msg):
    print(msg)
    def wrapper(fn):
        def new_wrapper(*args, **kwargs):
            print ("Before Calling %s" %fn.__name__)
            retval = fn(*args, **kwargs)
            # print ("After Calling %s" %fn.__name__)
            return retval
        return new_wrapper
    return wrapper
