# this file does not work - if you can fix it, please do so  - else delete it

from dataclasses import dataclass, fields
import multiprocessing as mp

man = mp.Manager()

@dataclass
class State: # iteration, total-iterations, status, result
    def clear(self):
        self.it = man.Value('i',0)
        self.nit = man.Value('i',0)
        self.status = man.Value('i', 0)
        self.result = man.dict({'out':"Not Computed Yet"})

    def __init__(self, *items):
        if len(items) == 4:
            self.it = items[0]
            self.nit = items[1]
            self.status = items[2]
            self.result = items[3]
        else:
            self.clear()
    # dynamically create getters and setters for all fields
        for t in [f.name for f in fields(self)]:
            exec(f"""
    @property
    def {t}(self):
        if type(self.{t}) == mp.managers.DictProxy:
            return self.{t}
        return self.{t}.value
    @{t}.setter
    def {t}(self,v):
        if type(self.{t}) == mp.managers.DictProxy:
            self.{t}.set('out',v)
        self.{t}.value = v
                    """)