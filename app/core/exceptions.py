from typing import Optional

class BaseAlreadyExistError(Exception):
    def __init__(self, entity_name: Optional[str], exception_name: str):
        self.entity_name = entity_name
        self.exception_name = exception_name
        self.detail = f'{self.exception_name.title()} already exists' if not self.entity_name else \
            f'{self.exception_name.title()}: {self.entity_name} already exists'
        super().__init__(self.detail)


class UserAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, email: str):
        super().__init__(entity_name=email, exception_name='User')


class LodgeAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, name: str):
        super().__init__(entity_name=name, exception_name='Lodge')

class RoomAlreadyExistError(BaseAlreadyExistError):
    def __init__(self, room_name: str):
        super().__init__(entity_name=room_name, exception_name='Room')

class ActiveLeaseFoundError(BaseAlreadyExistError):
    def __init__(self):
        super().__init__(exception_name='Lease')





class BaseNotFoundError(Exception):
    def __init__(self, name:str):
        self.detail = f'{name.title()} could not be found'
        
        
class UserNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name="User")

class LodgeNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='Lodge')


class RoomNotFoundError(BaseNotFoundError):
    def __init__(self):
        super().__init__(name='Room')


class UnauthorizedAccessError(Exception):
    def __init__(self):
        self.detail = f'Invalid email or password.'
        

    