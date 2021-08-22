
"""
This is needed because of issue in poetry scripts:-

https://github.com/python-poetry/poetry/issues/241#issuecomment-629754768

Otherwise we can just use:-

    poetry run siteplan run ...
"""
from siteplan.cli import main
main()
