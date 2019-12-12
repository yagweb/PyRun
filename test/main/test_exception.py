

def test_exception():
    raise Exception("mock exception to trigger on_error")


def on_error(loader, ex, tb):
    print("on_error from the main module")
    print(str(ex))


if __name__ == '__main__':
    test_exception()