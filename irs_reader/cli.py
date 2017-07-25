import sys

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    print("readxml, args='%s'" % args)
    
