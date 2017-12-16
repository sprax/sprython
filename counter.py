'''counter'''


def init_counter(count=0):
    '''(re)set counter that increments whenver called'''
    _count = count
    def _increment_counter():
        '''inner incrementer function'''
        nonlocal _count
        _count += 1
        return _count
    return _increment_counter

def main():
    '''test driver for init_counter'''
    counter = init_counter(6)
    print("counter() => ", counter())
    print("counter() => ", counter())

if __name__ == '__main__':
    main()