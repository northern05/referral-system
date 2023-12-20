import collections


def insert_pagination_info(response: dict, pagination: collections.namedtuple):
    response.update(pagination._asdict())


def paginate_list(list_to_paginate: list, pagination_spec: tuple):
    page_number = pagination_spec[0]
    page_size = pagination_spec[1]
    total_results = len(list_to_paginate)
    num_pages = (total_results + page_size - 1) // page_size
    start_index = (page_number - 1) * pagination_spec[1]
    end_index = min(start_index + page_size, total_results)
    paginated_response = list_to_paginate[start_index:end_index]
    _r = {
        "data": paginated_response,
        "num_pages": num_pages,
        "page_number": page_number,
        "page_size": page_size,
        "total_results": total_results
    }
    return _r
