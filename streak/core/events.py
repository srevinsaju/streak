from functools import wraps


def event_wrapper(event_type):
    print(event_type)

    if event_type == "create_account":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {
                    i: None
                    for i in [
                        "user_id",
                        "username",
                        "name",
                        "password",
                        "last_seen",
                        "last_checked_events",
                    ]
                }
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

        return decorator

    elif event_type == "create_task":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {
                    i: None
                    for i in [
                        "task_id",
                        "task_name",
                        "task_description",
                        "schedule",
                        "user_id",
                    ]
                }
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

    elif event_type == "create_streak":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {i: None for i in ["task_id", "user_id"]}
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

    elif event_type == "delete_streak":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {i: None for i in ["task_id", "user_id"]}
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

    elif event_type == "update_task":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {
                    i: None
                    for i in ["task_id", "task_name", "task_description", "schedule"]
                }
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

    elif event_type == "delete_task":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {i: None for i in ["task_id"]}
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

    elif event_type == "add_friend":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {i: None for i in ["user_uuid", "friend_uuid"]}
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

    elif event_type == "remove_friend":

        def decorator(func):
            @wraps(func)
            def original(*args, **kwargs):
                if "session" in kwargs:
                    del kwargs["session"]
                iterator = iter(args)
                try:
                    next(iterator)
                except StopIteration:
                    pass
                dct = {i: None for i in ["user_uuid", "friend_uuid"]}
                for key, value in zip(dct, iterator):
                    dct[key] = value
                dct.update(kwargs)
                print(dct)
                return func(*args, **kwargs)

            return original

    return decorator
