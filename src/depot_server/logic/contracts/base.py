from dataclasses import dataclass

class _Unset:
    pass

@dataclass(frozen=True)
class BaseContract:
    def to_kwargs(self, *args) -> dict:
        return {key: value for key, value in self.__dict__.items() if (not isinstance(value, _Unset) and key in args)}
    
    def to_named_kwargs(self, **kwargs) -> dict:
        return {kwargs[key]: value for key, value in self.__dict__.items() if (not isinstance(value, _Unset) and key in kwargs)}

    def all_to_kwargs(self) -> dict:
        return {key: value for key, value in self.__dict__.items() if not isinstance(value, _Unset)}