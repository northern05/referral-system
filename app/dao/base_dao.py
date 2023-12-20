import sqlalchemy_filters

from app import db
from app import exceptions


class BaseDAO:

    def __init__(
            self,
            model,
            default_sort_field: str = 'created_at',
            default_sort_direction: str = 'desc'
    ):
        self.model = model
        self.default_sort_field = default_sort_field
        self.default_sort_direction = default_sort_direction

    def get_all(
            self,
            filter_spec: list,
            sort_spec: list,
            pagination_spec: tuple,
    ) -> (list, tuple):
        if not sort_spec:
            sort_spec = [{
                "model": self.model.__name__,
                "field": self.default_sort_field,
                "direction": self.default_sort_direction
            }]

        query = db.session.query(self.model)
        query = sqlalchemy_filters.apply_filters(
            query=query, filter_spec=filter_spec
        )
        query = sqlalchemy_filters.apply_sort(
            query=query, sort_spec=sort_spec,
        )
        pagination = None
        if pagination_spec:
            query, pagination = sqlalchemy_filters.apply_pagination(
                query=query, page_number=pagination_spec[0], page_size=pagination_spec[1])
        return query, pagination

    def get_selected(
            self,
            id: int = None,
            filter_spec: list[dict] = None,
            is_raiseable: bool = True
    ):
        if id:
            query = self.model.query.get(id)
        elif filter_spec:
            query = db.session.query(self.model)
            query = sqlalchemy_filters.apply_filters(
                query=query, filter_spec=filter_spec
            ).first()
        else:
            raise exceptions.BadAPIUsage

        if not query or hasattr(self.model, 'state') and query.state == 'deleted':
            if is_raiseable:
                raise exceptions.ContentNotFound(f"{self.model=} not found")

        return query

    def create(self, auto_commit: bool = True, **kwargs):
        intent = self.model(**kwargs)
        db.session.add(intent)
        if auto_commit: db.session.commit()
        return intent

    def update(self, id: int, new_data: dict, auto_commit: bool = True):
        intent = self.get_selected(id=id)
        for k, v in new_data.items():
            if hasattr(self.model, k) and v is not None:
                setattr(intent, k, v)

        if auto_commit: db.session.commit()
        return intent

    def delete(
            self,
            id: int = None,
            filter_spec: list[dict] = None,
            auto_commit: bool = True
    ):
        db.session.delete(self.model.query.get(id))
        if auto_commit: db.session.commit()
        return True

    @staticmethod
    def commit():
        db.session.commit()
