def generate_lazy_val(func):
    saved_value = None
    called = False

    def lazy_holder():
        nonlocal called, saved_value
        if called:
            return saved_value
        else:
            saved_value = func()
            called = True
            return saved_value

    return lazy_holder


def fixed_point(v, f, good_enough):
    history = []
    while True:
        v2 = f(v)
        if good_enough(v, v2):
            return v
        if v2 in history:
            for debug_v2 in history:
                print(debug_v2)
            raise AssertionError("Failed: fixedPoint encountered the same value twice:", v2)
        else:
            history.append(v)
            v = v2


def find_simplifier(self, simplifiers):
    """simplifiers is a list of 0-ary functions.
    Calling such a function either returns `this` or something else.
    We call all the functions in turn, as long as they return `this`.
    As soon as such a function returns something other than `this`,
    then that new value is returned from find_simplifier.
    As a last resort, `this` is returned."""

    for s in simplifiers:
        out = s()
        if self != out:
            return out
    return self


def uniquify(seq):
    """remove duplicates from a list, but preserve the order.
    If duplicates occur in the given list, then left-most occurrences
    are removed, so that the right-most occurrence remains.
    E.g., uniquify([1,2,3,2]) --> [1,3,2]"""
    from collections import OrderedDict

    return list(reversed(list(OrderedDict.fromkeys(reversed(seq)))))


def flat_map(f, xs):
    return [y for z in xs for y in f(z)]


def search_replace_splice(xs, search, replace):
    def select(x):
        if x == search:
            return replace
        else:
            return [x]
    return flat_map(select, xs)


def search_replace(xs, search, replace):
    return search_replace_splice(xs, search, [replace])


def remove_element(xs, search):
    return search_replace_splice(xs, search, [])


# find first element of list which makes the predicate true
# if no such element is found, return the given default or None
def find_first(pred, xs, default=None):
    return next(filter(pred, xs), default)
