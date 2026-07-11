import contextlib

class ContextManagers:
    def __init__(self, cms):
        self.cms = cms
        self.stack = contextlib.ExitStack()
        
    def __enter__(self):
        for cm in self.cms:
            self.stack.enter_context(cm)
        return self
        
    def __exit__(self, *args, **kwargs):
        self.stack.__exit__(*args, **kwargs)
