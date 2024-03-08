# --- Imports Python Modules into instance
from flask import Flask, jsonify, request, make_response
from bson.objectid import ObjectId
from pymongo import MongoClient
import jwt
import datetime
from functools import wraps
import bcrypt
import uuid
from flask_cors import CORS

# --- Flask Instance --- 
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "i_am_a_secret"


# --- AUTH0 Connection ---
AUTH0_DOMAIN = 'dev-d1zglhvx0fh44i2n.us.auth0.com'
AUTH0_CLIENT_ID = 'dAdbXIxIgp7wThua7ByaCwM4Tht1eCKz'
AUTH0_CLIENT_SECRET = 'BvZB7CEpxFjbVTu1X8D1PvwdH3xDUXIv1AiTzI-AWOHjcmEgfFJYKoW4H0_a-P6K'
AUTH0_API_IDENTIFIER = 'https://dev-d1zglhvx0fh44i2n.us.auth0.com/api/v2/'

AUTH0_API_URL = 'https://dev-d1zglhvx0fh44i2n.us.auth0.com/api/v2/'

# --- MongoDB Connection --- 
client = MongoClient("localhost", 27017)
db = client["AnimeDirect"]
anime_collection = db["animeList"]
staff_collection = db["staff"]
blacklist = db.blacklist

staff_list = [
    {
        "name": "Ethan McFarlane",
        "username": "McFarlane-E1",
        "password": b"mcfar_e",
        "admin": True
    },
    {
        "name": "Ethan McFarlane1",
        "username": "McFarlane-E2",
        "password": b"mcfar_m",
        "admin": False
    }
]

for new_staff_user in staff_list:
    new_staff_user["password"] = \
        bcrypt.hashpw(new_staff_user["password"], \
                    bcrypt.gensalt())
    staff_collection.insert_one(new_staff_user)

# --- Authorization token --- 
def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode( token, app.config['SECRET_KEY'] )
        except:
            return jsonify({'message': 'Invalid token'}), 401
        
        bl_token = blacklist.find_one({"token": token})
        if bl_token is not None:
            return make_response(jsonify({'message': 'Token has been cancelled'}), 401)
        return func(*args, **kwargs)
    
    return jwt_required_wrapper

# --- Admin Required ---
def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = jwt.decode(token, app.config['SECRET_KEY'])
        if data["admin"]:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({'message': 'Admin Access Required'}), 401)
    return admin_required_wrapper

# --- Anime List Endpoint ---
@app.route("/api/anime", methods = ["GET"])
def show_all_anime():
    page_num, page_size = 1, 10
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = (page_size * (page_num - 1))

    data_to_return = []
    for anime in anime_collection.find() \
                 .skip(page_start).limit(page_size):
        anime['_id'] = str(anime['_id'])
        for review in anime['reviews']:
            review['_id'] = str(review['_id'])
        data_to_return.append(anime)
    return make_response( jsonify(data_to_return), 200)

# --- Showing One Anime Endpoint ---
@app.route("/api/anime/<string:id>", methods = ['GET'])
def show_one_anime(id):
    anime = anime_collection.find_one({'_id': ObjectId(id)})
    if anime is not None:
        anime['_id'] = str(anime['_id'])
        for review in anime['reviews']:
            review['_id'] = str(review['_id'])
        return make_response( jsonify([anime]), 200)
    else:
        return make_response( jsonify({"error": "Invalid anime ID"}))

# --- Showing Reviews Endpoint ---
@app.route("/api/anime/<string:id>/reviews", methods = ['GET'])
def fetch_all_reviews(id):
    data_to_return = []
    anime = anime_collection.find_one( { "_id": ObjectId(id) }, { "reviews": 1, "_id": 1 })
    for review in anime["reviews"]:
        review["_id"] = str(review["_id"])
        data_to_return.append(review)
    return make_response( jsonify( data_to_return ), 200)
    
# --- Adding Reviews ---
@app.route("/api/anime/<string:id>/reviews", methods=["POST"])
def add_new_review(id):
    new_review = {
        "_id": ObjectId(id),
        "username": request.form['username'],
        "review": request.form['review'],
        "stars": request.form['stars']
    }
    anime_collection.update_one({"_id": ObjectId(id)}, {"$push": {"reviews": new_review }})
    new_review_link = "http://localhost:5000/api/anime/"+id+"/reviews"
    return make_response( jsonify({"url": new_review_link}), 201)

# --- Editing Anime ---
@app.route("/api/anime/<string:id>", methods=['PUT'])
@jwt_required
@admin_required
def edit_anime(id):
    if "title" in request.form and "title_english" in request.form:
        result = anime_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"title": request.form["title"],
                      "title_english": request.form["title_english"]
                     }
            })
        if result.matched_count == 1:
            edited_anime_link = "http://localhost:5000/api/anime/" + id
            return make_response( jsonify({"url": edited_anime_link}), 200)
        else:
            return make_response( jsonify({"error": "Invalid anime id"}), 404)
    else:
        return make_response( jsonify({"error": "Missing form data"}), 404)
    
# --- Add Anime ---
@app.route("/api/anime", methods = ['POST'])
@jwt_required
@admin_required
def add_anime():
    if "anime_id" in request.form and \
        "title" in request.form and \
        "title_english" in request.form and \
        "image_url" in request.form and \
        "type" in request.form and \
        "source" in request.form and \
        "episodes" in request.form and \
        "status" in request.form and \
        "aired_string" in request.form and \
        "aired" in request.form and \
        "duration" in request.form and \
        "producer" in request.form and \
        "studio" in request.form and \
        "genre" in request.form:
        new_anime = {
            "anime_id": request.form["anime_id"],
            "title": request.form["title"],
            "title_english": request.form["title_english"],
            "image_url": request.form["image_url"],
            "type": request.form["type"],
            "source": request.form["source"],
            "episodes": request.form["episodes"],
            "status": request.form["status"],
            "aired_string": request.form["aired_string"],
            "aired": request.form["aired"],
            "duration": request.form["duration"],
            "producer": request.form["producer"],
            "studio": request.form["studio"],
            "genre": request.form["genre"],
            "reviews": []
            }
        anime_collection.insert_one(new_anime)
        return make_response( jsonify({"message": "Anime added successfully"}), 201)
    else:
        return make_response( jsonify({"error": "Missing form data"}), 404)

    
# --- Deleting Anime ---
@app.route("/api/anime", methods = ['DELETE'])
@jwt_required
@admin_required
def delete_anime():
    if "anime_id" in request.form and \
        "title" in request.form and \
        "title_english" in request.form:
        remove_anime = {
            "anime_id": request.form["anime_id"],
            "title": request.form["title"],
            "title_english": request.form["title_english"],
            }
        anime_collection.delete_one(remove_anime)
        return make_response( jsonify({}), 204)
    else:
        return make_response( jsonify({"error": "Missing form data"}), 404)

# --- Backend Login Endpoint ---
@app.route('/api/login', methods=['GET'])
def login():
    auth = request.authorization
    if auth:
        user = staff_collection.find_one({'username': auth.username})
        if user is not None:
            if bcrypt.checkpw(bytes(auth.password, 'UTF-8'), \
                              user["password"]):
                token = jwt.encode( \
                    {'user': auth.username,
                     'admin': user["admin"],
                     'exp': datetime.datetime.utcnow() + \
                        datetime.timedelta(minutes=30)
                    }, app.config['SECRET_KEY'])
                return make_response(jsonify({'token': token.decode('UTF-8')}), 200)
            else:
                return make_response(jsonify({'message': 'Bad Password'}), 401)
        else:
            return make_response(jsonify({'message': 'Bad Username'}), 401)
    return make_response(jsonify({'message': 'Authentication Required'}), 401 )

# --- Logout Endpoint ---
@app.route('/api/logout', methods=["GET"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist.insert_one( { "token": token } )
    return make_response( jsonify( { 'message': 'Logout successful' } ), 200 )

if __name__ == "__main__":
    app.run(debug=True)