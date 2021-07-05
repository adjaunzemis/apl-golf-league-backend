r"""
APL golf league data server

Authors
-------
Andris Jaunzemis

"""

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS

from apl_golf_league_database import APLGolfLeagueDatabase
from golf_course import GolfCourse

class Courses(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, default=None, required=False, help='Course identifier')
        parser.add_argument('name', type=str, default=None, required=False, help='Course name')

        args = parser.parse_args()
        course_id = args['id']
        name = args['name']

        db = APLGolfLeagueDatabase('./config/admin.user', verbose=False)
        courses = db.get_courses(course_id=course_id, name=name, verbose=False)
        if courses is None:
            return []
        return [course.as_dict() for course in courses]

    def post(self):
        course_data = request.get_json(force=True)
        course = GolfCourse.from_dict(course_data)

        db = APLGolfLeagueDatabase('./config/admin.user', verbose=False)
        db.put_course(course, verbose=True)
        
class APLGolfLeagueServer(object):

    def __init__(self, port=3000, debug=False):
        self._app = Flask(__name__)
        self._api = Api(self._app)
        CORS(self._app)
        self.add_endpoints()
        self.run(port, debug=debug)

    def add_endpoints(self):
        self._api.add_resource(Courses, '/api/courses')

    def run(self, port, debug=False):
        self._app.run(port=port, debug=debug)

if __name__ == "__main__":
    server = APLGolfLeagueServer(port=3000, debug=False)
