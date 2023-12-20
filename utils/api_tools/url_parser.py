"""
    This file has implementation of common usage functions for parsing URL args in the project.
    URL params (+ ..._spec_options) are used as an input for these functions.

    Contained functions:
       * get_filters
       * get_datetime_period_filters
       * get_price_range_filters
       * get_sort_params
       * get_pagination
"""
from datetime import datetime, timedelta
from utils import general


def get_filters(
        url_args: dict,
        filter_spec_options: dict
) -> list:
    filter_spec = []
    try:
        for k, v in url_args.items():
            if k in filter_spec_options.keys() and v is not None:
                if v in ('false', 'False', 'true', 'True'):
                    v = general.str2bool(v)
                filter_spec.append({
                    "model": filter_spec_options[k]["model"],
                    "field": filter_spec_options[k]["field"],
                    "op": "in" if isinstance(v, str) and "%" in v else "==",
                    "value": v.split("%") if isinstance(v, str) and "%" in v else v
                })
    except KeyError:
        raise ValueError("Incorrect filter parameters")
    return filter_spec


def get_datetime_period_filters(
        url_args: dict,
        timeperiod_filter_spec_options: dict,
        precise: bool = False
) -> list:
    """

    :param precise: decides which date format to convert
    :param url_args: dict like
    :param timeperiod_filter_spec_options: {public_arg_name: {"model":"Model", "field": "date_field"}, ...}
    :return: filter_spec
    """
    filter_spec = []
    date_format = "%Y_%m_%d:%H_%M" if precise else "%Y_%m_%d"
    # + timedelta(days=1, microseconds=-1) is needed to add 23:59:59.9999
    # to end period to include this day for not precise datetimes
    delta = timedelta(seconds=1) if precise else timedelta(days=1, microseconds=-1)
    try:
        for k, v in url_args.items():  # process all periods in URL
            if k in timeperiod_filter_spec_options.keys() and v is not None:  # check for param capability
                start_period, end_period = v.split('-')

                # add start period
                filter_spec.append({
                    "model": timeperiod_filter_spec_options[k]["model"],
                    "field": timeperiod_filter_spec_options[k]["field"],
                    "op": ">=" if start_period else "is_not_null",
                    "value": datetime.strptime(start_period, date_format) if start_period else ""
                })
                # add end period
                filter_spec.append({
                    "model": timeperiod_filter_spec_options[k]["model"],
                    "field": timeperiod_filter_spec_options[k]["field"],
                    "op": "<=" if end_period else "is_not_null",
                    "value": datetime.strptime(end_period, date_format) + delta if end_period else ""
                })
    except KeyError:
        raise ValueError("Incorrect datetime parameters")
    return filter_spec


def get_sort_params(
        url_args: dict,
        sort_spec_options: dict
) -> list:
    """

    :param url_args:  dict like
    :param sort_spec_options: {"nftCount_": {"model": "Nft", "field": "current_owner_id"}, ...}
    :return: sort_spec - list of dicts
    """
    try:
        sort_spec = [
            {
                "model": sort_spec_options[k]["model"],
                "field": sort_spec_options[k]["field"],
                "direction": v
            } for k, v in url_args.items() if k in sort_spec_options.keys() and v is not None]
    except KeyError:
        raise ValueError("Incorrect sort parameters")

    return sort_spec


def get_pagination(
        url_args: dict,
        default_page_number: int = 1,
        default_page_size: int = 100
) -> tuple:
    """
        This function pars "page_number" and "page_size" from given URL args
    :param url_args: args from request
    :param default_page_number: default optional
    :param default_page_size: default optional
    :return: pagination_spec list like [page_number, page_size]
    """
    try:
        page_number = int(url_args.get("page_number", default_page_number))
        page_size = int(url_args.get("page_size", default_page_size))
    except Exception:
        raise ValueError("Incorrect pagination parameters")
    if page_number <= 0 or page_size <= 0:
        raise ValueError("Incorrect pagination parameters")
    if page_size > 100:
        raise ValueError("The maximum value of page_size is 50")
    return page_number, page_size
