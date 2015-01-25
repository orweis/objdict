import collections
import copy
import inspect 

__author__ = 'OW'


class AttrObj(object):
    __slots__ = []

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

    def __getattr__(self, name):
        print "aaa", name
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    __setattr__ = dict.__setitem__
    __iter__ = dict.iteritems

class AttrDict(AttrObj, dict):
    pass


def split_dict(d, key_groups, dict_type = dict ):
    """
    @param d a dictionary to split
    @param key_groups a list of key groups (e.g. [(1,2,3),  ("a", "b", 6)] to split according to
    @return a list of dictionaries , each dict containing the keys of one given group and the matching values from the original dict;
            keys that weren't set in a group, will be part of the last 'left-overs' group.
    """
    # Final outcome split
    result = []
    # Track which keys got a new group
    handled_keys = set()
    #For every group
    for key_group in key_groups:
        # Create a new key
        outcome_dict = dict_type()
        #Using the given keys
        for key in key_group:
            outcome_dict[key] = d[key]
            handled_keys.add(key)
        result.append(outcome_dict)
    # Take all unhandled keys as a new group
    last_outcome_dict = dict_type()
    for unhandled_key in handled_keys.symmetric_difference(d.keys()):
        last_outcome_dict[unhandled_key] = d[unhandled_key]
    result.append(last_outcome_dict)
    # Return the list of new dictionaries
    return result


class Rdict(dict):
    """
    A dict that support recursive updates (i.e. recursive update of internal dicts and lists)
    dicts get updated (keys inserted) lists get appended with the new value

    # Setting item hierarchy example:
        >>> a = Rdict()
        >>> a["Key"]["AnotherKey"]["YetAnotherKey"] = 8
        >>> print(a)
        {'Key': {'AnotherKey': {'YetAnotherKey': 8}}}

    # Updating example
        >>> o1 = Rdict({1: {2: ["a","b"]} })
        >>> o2 = Rdict({1: {2: ["c","d"], "2.1" : "String" } })
        >>> o1.update(o2)
        >>> o1.update(o2)
        >>> print(o1)
        {1: {2: ['a', 'b', 'c', 'd'], '2.1': 'String'}}
    """

    def __init__(self, *args, **kwargs):
        super(Rdict, self).__init__(*args, **kwargs)
        # The internal type used to init children dicts
        # Default is the current class
        self.__dict_type = self.__class__

    def __getitem__(self, item):
        result = super(Rdict, self).get(item, self.__dict_type())
        if isinstance(result, Rdict) and len(result) == 0:
            self[item] = result
        return result

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, Rdict):
            value = self.__dict_type(value)
        return super(Rdict, self).__setitem__(key, value)

    def _updateSubMap(self, k, v):
        #Make sure internal mappings are also Rdicts
        if not isinstance(self[k], Rdict):
            self[k] = self.__dict_type(self[k])
            #Recurs on internal value
        self[k].update(v)

    def _updateSubList(self, k, v):
        self[k] += v

    def update(self, E=None, **F):
        if E is None:
            E = F
        for k, v in E.iteritems():
            is_update_able = False
            if isinstance(v, collections.Mapping):
                #If we already have a value for the given key
                if k in self:
                    curValue = self[k]
                    if isinstance(curValue, collections.Mapping):
                        self._updateSubMap(k, v)
                        is_update_able = True
                    # Lists automatically extend on updates
                    elif isinstance(curValue, list) and isinstance(v, list):
                        self._updateSubList(k, v)
                        is_update_able = True
            elif k in self and isinstance(self[k], list) and isinstance(v, list):
                self[k] += v
                is_update_able = True
            #If current value isn't a mapping
            #Just override
            if not is_update_able:
                self[k] = copy.deepcopy(v)



class Objdict (AttrObj, Rdict):
    
    # ignore builtins and IDE frequently used attribute checks
    __ignored_keys__ = {"__class__","__dict__","__members__","__methods__","_oleobj_","_obj_"}

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

    def __getattr__(self, name):
        # Ignore selected attribute names- treating them as real attributes only 
        if name in Objdict.__ignored_keys__:
            return Rdict.__getattr__(self, name)
        else:
            return AttrObj.__getattr__(self, name)

    def __getattribute__(self, name):
        print name
        # Ignore selected attribute names- treating them as real attributes only 
        if name in Objdict.__ignored_keys__:
            return Rdict.__getattribute__(self, name)
        else:
            return AttrObj.__getattribute__(self, name)

    def split(self, key_groups):
        """
        @param key_groups a list of key groups (e.g. [(1,2,3),  ("a", "b", 6)] to split according to
        @return a list of dictionaries , each dict containing the keys of one given group and the matching values from the original dict;
                keys that weren't set in a group, will be part of the last 'left-overs' group.
        """
        return split_dict(self, key_groups, dict_type=self.__class__)





class OrderedMap(collections.OrderedDict):
    """
    @see http://stackoverflow.com/questions/7878933/is-possible-to-override-the-notation-so-i-get-an-ordereddict-instead-of/25889274#25889274
    """
    def __getitem__(self, index):
        if isinstance(index, slice):
            self[index.start] = index.stop
            return self
        else:
            return collections.OrderedDict.__getitem__(self, index)

    def __add__(self,other):
        self.update(other)
        return self

