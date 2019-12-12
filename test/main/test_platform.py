import platform


def test_platform():    
    print(platform.__file__)


def on_error(loader, ex, tb):
    print("on_error from the main module")
    print(str(ex))


if __name__ == '__main__':
    test_platform()