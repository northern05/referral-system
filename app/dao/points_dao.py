from app.models import Points
from app.dao.base_dao import BaseDAO
from app import db


class PointsDAO(BaseDAO):

    def get_points_by_user(self, user_id: int):
        return db.session.query(self.model) \
            .filter(Points.user_id == user_id) \
            .first()


points_dao = PointsDAO(Points)
