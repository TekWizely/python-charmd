#!/usr/bin/env python3
if __name__ == '__main__':
    import sys, os
    print(sys.path)
    # path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    # print(path)
    # sys.path.append(path)
    from src.pychmdbg.__main__ import main
    if sys.argv[0].endswith('.exe'):
        sys.argv[0] = sys.argv[0][:-4]
    sys.exit(main())
