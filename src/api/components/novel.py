from apistar import Route
from apistar.http import Request, RequestData, JSONResponse, Response
from apistar.exceptions import Forbidden


def get_category_book(category: str):
    pass


def get_book_info(bid: str):
    pass


def get_book_all_chapter(bid: str):
    pass


def get_chapter(cid: str):
    pass


routes = [
    Route('/book/{bid}', method='GET', handler=get_book_info),
]

if __name__ == '__main__':
    pass
