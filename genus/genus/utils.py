def generate_lazy_val(func, vargs):
    
    def lazy_holder():
        if not lazy_holder.was_called:
            lazy_holder.held = lazy_holder.work(lazy_holder.vargs)
            lazy_holder.was_called = True
        return lazy_holder.held
    
    lazy_holder.was_called = False
    lazy_holder.held = None
    lazy_holder.work = func
    lazy_holder.vargs = vargs
    
    return lazy_holder