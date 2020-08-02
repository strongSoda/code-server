from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import exc
from flask_cors import CORS

# configs
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///coda'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# models
class UsersModel(db.Model):
    __tablename__ = 'users'

    googleId = db.Column(db.String(), primary_key=True)
    firstName = db.Column(db.String())
    lastName = db.Column(db.String())
    email = db.Column(db.String())
    voted = db.Column(db.Boolean())

    def __init__(self, googleId, firstName, lastName, email):
        self.googleId = googleId
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.voted = False

    def __repr__(self):
        return f"<User {self.googleId}>"


class CandidatesModel(db.Model):
    __tablename__ = 'candidates'

    candidate_id = db.Column(db.String(), primary_key=True)
    candidate_passcode = db.Column(db.String())
    name = db.Column(db.String())
    number_challenges_solved = db.Column(db.String())
    expertise = db.Column(db.Integer())
    expert_in = db.Column(db.JSON())
    votes = db.Column(db.Integer())

    def __init__(self, candidate_id, candidate_passcode, name, number_challenges_solved, expertise, expert_in):
        self.name = name
        self.candidate_id = candidate_id
        self.candidate_passcode = candidate_passcode
        self.number_challenges_solved = number_challenges_solved
        self.expert_in = expert_in
        self.expertise = expertise
        self.votes = 0

    voted = db.Column(db.Boolean())

    def __repr__(self):
        return f"<Candidate {self.googleId}>"


# routes
@app.route('/')
def home():
    return 'hello world'


@app.route('/admin/candidates/add/')
def admin_add_candidate():
    admins = ["a001"]
    admin_code = request.args.get('admin_code')
    if admin_code not in admins:
        return -2
    name = request.args.get('name').lower()
    candidate_id = request.args.get('candidate_id')
    candidate_passcode = request.args.get('candidate_passcode')
    number_challenges_solved = request.args.get('number_challenges_solved')
    expertise = request.args.get('expertise')
    expert_in = request.args.get('expert_in')

    new_candidate = CandidatesModel(
        candidate_id=candidate_id, name=name, candidate_passcode=candidate_passcode, number_challenges_solved=number_challenges_solved, expert_in=expert_in, expertise=expertise)
    try:
        db.session.add(new_candidate)
        db.session.commit()
    except exc.IntegrityError:
        # db.session.rollback()
        return jsonify(-2)
    return jsonify(new_candidate.candidate_id)


@app.route('/candidates/')
def get_candidates():
    result = CandidatesModel.query.all()
    return jsonify([{
        'name': candidate.name,
        "id": candidate.candidate_id,
        "votes": candidate.votes,
        "expertise": candidate.expertise,
        "number_challenges_solved": candidate.number_challenges_solved,
        "expert_in": candidate.expert_in
    } for candidate in result])


@app.route('/users/add/')
def add_User():
    firstName = request.args.get('first_name').lower()
    googleId = request.args.get('googleId')
    lastName = request.args.get('last_name').lower()
    email = request.args.get('email').lower()

    new_user = UsersModel(
        googleId=googleId, firstName=firstName, lastName=lastName, email=email)
    try:
        db.session.add(new_user)
        db.session.commit()
    except exc.IntegrityError:
        # db.session.rollback()
        return jsonify(-2)
    return jsonify(new_user.googleId)


@app.route('/vote/')
def vote():
    candidate_id = request.args.get('candidate_id')
    googleId = request.args.get('googleId')
    candidate = CandidatesModel.query.get(candidate_id)
    candidate.votes = candidate.votes + 1
    user = UsersModel.query.get(googleId)
    user.voted = True
    db.session.commit()
    return jsonify(user.googleID)


@app.route('/users/voted/')
def check_vote():
    googleId = request.args.get('googleId')
    user = UsersModel.query.get(googleId)
    return jsonify(user.voted)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
