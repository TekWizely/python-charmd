#!/usr/bin/env python3
if __name__ == "__main__":
    import sys

    from src.charmd.__main__ import main

    if sys.argv[0].endswith(".exe"):
        sys.argv[0] = sys.argv[0][:-4]
    sys.exit(main())
