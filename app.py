from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text, Date
from werkzeug.utils import secure_filename
import os
import uuid
import time

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music_streaming_database.db'
app.config['UPLOAD_FOLDER'] = 'static/audio'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# -------------------------- MODELS -------------------------------------
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100) , nullable =False)
    is_active = db.Column(db.Integer , default =1)

class songs(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    songname = db.Column(db.String(100), unique=True, nullable=False)
    releasedate = db.Column(Date)
    lyrics = db.Column(db.Text)
    singer= db.Column(db.String(100))
    uploadedby = db.Column(db.Integer , nullable = False)
    filename = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    averagerating = db.Column(db.Integer , default =0)
    ratingcount = db.Column(db.Integer, default =0 )
    is_active = db.Column(db.Integer, default=1)

class creatoralbum(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.Integer , nullable = False)
    album_name =db.Column(db.Integer , nullable = False)
    albumratings =db.Column(db.Integer , default =0)
    albumratingcount = db.Column(db.Integer , default =0)
    is_active = db.Column(db.Integer, default=1)

class albumdetails (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    albumid = db.Column(db.Integer, nullable=False)
    songid = db.Column(db.Integer, nullable=False)

class ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    songid = db.Column(db.Integer, nullable=False)
    ratedby = db.Column(db.String, nullable=False)
    ratingvalue = db.Column(db.Integer, default =0)

class genres(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genrename = db.Column(db.String(120), unique=True, nullable=False)

class useralbum(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.Integer , nullable = False)
    album_name =db.Column(db.Integer , nullable = False)


class useralbumdetails (db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    albumid = db.Column(db.Integer, nullable=False)
    songid = db.Column(db.Integer, nullable=False)

class admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100) , nullable =False)


#--------------------------- COMMON ROUTES -------------------------------

@app.route('/' , methods=[ 'GET'])
def index():
    return render_template('index.html')
@app.route('/user/register',methods=['POST', 'GET'])
def register():
    if request.method =='POST':
        name =request.form['name']
        userid = request.form['userid']
        email = request.form['email']
        password = request.form['password']
        if (name ==None or userid ==None or email ==None or password ==None   ):
            msg = f"You can not leave a field empty"
            return render_template('register.html' , message=msg)
        condition = user.query.filter_by(username=userid).first()
        if condition:
            msg = f"User Already Exists"
            return render_template('register.html', message=msg)

        new_user = user(
            name=name,
            username=userid,
            email=email,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('user_home' , userid = userid , page =1))
    return render_template('register.html' , message =None)


@app.route('/user/login',methods=['POST', 'GET'])
def user_login():
    if request.method =='POST':
        userid = request.form['userid']
        password = request.form['password']
        user1 = user.query.filter_by(username=userid).first()
        if user1 ==None:
            msg = f"No User Found Please Register"
            return render_template('/user/login.html', message=msg)
        if password != user1.password:
            msg = f"Incorrect Password! Try Again"
            return render_template('/user/login.html', message=msg)
        return redirect(url_for('user_home', userid =userid , page =1))
    return render_template('/user/login.html' , message =None)






#--------------------------- CREATOR ROUTES -------------------------------


@app.route('/creator/home/<userid>',methods=['GET'])
def creator_home(userid):
    totalsongs = songs.query.filter_by(uploadedby=userid , is_active=1).count()
    allsongs = songs.query.filter_by(uploadedby=userid , is_active=1).all()
    albums = creatoralbum.query.filter_by(author = userid , is_active=1).all()
    totalalbums = creatoralbum.query.filter_by(author = userid , is_active =1).count()
    averagerating =0
    ratingcount=0
    for song in allsongs:
        averagerating += (round(song.averagerating * song.ratingcount))
        ratingcount += song.ratingcount
    if ratingcount:
        averagerating /=ratingcount
    else :
        averagerating =0
    if totalsongs:
        return render_template('/creator/home.html', userid =userid , totalsongs = totalsongs , songs = allsongs , albums = albums , totalalbums =totalalbums , averagerating = averagerating)
    return render_template('/creator/home.html', userid =userid , totalsongs = None  , songs = None , albums =albums , totalalbums =totalalbums , averagerating = averagerating)


@app.route('/lyrics/<id>/<userid>',methods=['GET'])
def viewlyrics(id, userid):
    song = songs.query.filter_by(id=id , is_active=1).first()
    if song:
        filename = song.filename
        lyrics = song.lyrics
        return render_template('/creator/lyrics.html',  lyrics = lyrics , filename = filename , userid =userid , id = id)
    return "No Existing song found"

@app.route('/song/delete/<id>/<userid>',methods=['GET'])
def deletesong(id, userid):
    song = songs.query.filter_by(id=id).first()
    if song:
        if (song.uploadedby == userid):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], song.filename))
            genre = song.genre
            db.session.delete(song)
            db.session.commit()
            val = songs.query.filter_by(genre = genre).first()
            if val==None:
                genres.query.filter_by(genrename  =genre).delete()
            albumdetails.query.filter_by(songid =id).delete()
            db.session.commit()
            ratings.query.filter_by(songid =id).delete()
            db.session.commit()
            useralbumdetails.query.filter_by(songid =id).delete()
            return redirect(url_for('creator_home' , userid =userid))
        return "You do not have permission to delete this song"
    return "No Existing song found"


@app.route('/song/edit/<id>/<userid>',methods=['GET', 'POST'])
def editsong(id, userid):
    if request.method =='GET':
        song = songs.query.filter_by(id=id).first()
        if song:
            return render_template('/creator/editsong.html' , song = song , userid = userid , id = id )
        return "No songs"
    song = songs.query.filter_by(id=id).first()
    title = request.form['title']
    singer = request.form['singer']
    date = request.form['releaseDate']
    lyrics = request.form['lyrics']
    genre = request.form['genre']
    uploadedby = userid
    releaseDate = datetime.strptime(date, '%Y-%m-%d').date()
    if song:
        prevge = song.genre
        song.songname = title
        song. releasedate = releaseDate
        song.lyrics = lyrics
        song.singer = singer
        song.genre = genre
        song.uploadedby = uploadedby
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], song.filename))
                filename = get_unique_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                song.filename = filename
        db.session.commit()
        val = songs.query.filter_by(genre=prevge).first()
        if val == None:
            genres.query.filter_by(genrename=prevge).delete()
        return redirect(url_for('creator_home' , userid =userid))
    return "No song found"

def get_unique_filename(filename):
    _, file_extension = os.path.splitext(filename)
    unique_filename = str(uuid.uuid4()) + '_' + str(int(time.time())) + file_extension
    return secure_filename(unique_filename)

@app.route('/creator/uploadsong/<userid>',methods=['POST', 'GET'])
def uploadsong(userid):
    if request.method == 'POST':
        title = request.form['title']
        singer = request.form['singer']
        date = request.form['releaseDate']
        lyrics = request.form['lyrics']
        uploadedby = userid
        genre = request.form['genre']
        releaseDate =datetime.strptime(date, '%Y-%m-%d').date()
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = get_unique_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                song1 = songs(
                    songname=title,
                    releasedate = releaseDate,
                    lyrics = lyrics,
                    singer = singer,
                    uploadedby = uploadedby,
                    filename = filename,
                    genre = genre
                )
                ge = genres.query.filter_by(genrename=genre).first()
                if ge==None:
                    newgenre = genres(genrename = genre)
                    db.session.add(newgenre)
                    db.session.commit()
                db.session.add(song1)
                db.session.commit()
                return redirect(url_for('creator_home', userid = userid))
            return ("Invalid filename")
        return ("No file found")
    return render_template('/creator/songupload.html' , userid = userid)


@app.route('/creator/createalbum/<userid>',methods=['POST', 'GET'])
def createalbum(userid):
    if request.method == 'POST':
        albumname = request.form['albumname']
        author = userid
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
        creatoralbum1 = creatoralbum(
            author =author,
            album_name = albumname
        )
        db.session.add(creatoralbum1)
        db.session.commit()
        albumid = creatoralbum1.id
        songid =request.form.getlist('selected_songs')
        for xid in songid:
            albumdetails1 = albumdetails(
                albumid=albumid,
                songid=xid
            )
            db.session.add(albumdetails1)
        db.session.commit()
        return redirect(url_for('creator_home' , userid = userid))
    song = songs.query.filter_by(uploadedby = userid)
    return  render_template('/creator/createalbum.html' , songs = song, userid = userid)


@app.route('/creator/viewalbum/<userid>/<albumid>',methods=['GET'])
def viewalbum(userid, albumid):
        user1 = user.query.filter_by(username=userid, is_active=1).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
        album = creatoralbum.query.filter_by(id =albumid , is_active=1 ).first()
        if album==None:
            msg = f"No Album found Please Create One "
            return msg
        albumdetail = albumdetails.query.filter_by(albumid = albumid , is_active=1).all()
        songss =[]
        for item in albumdetail:
            song = songs.query.filter_by(id = item.songid).first()
            if song:
                songss.append(song)
        return render_template('/creator/viewalbum.html' , userid = userid , songs = songss , albumname =album.album_name , albumid = albumid )


@app.route('/creator/deletealbum/<userid>/<albumid>',methods=['GET'])
def deletealbum(userid, albumid):
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
        album = creatoralbum.query.filter_by(id =albumid )
        if album==None:
            msg = f"No Album found Please Create One "
            return msg
        albumdetails.query.filter_by(albumid=albumid).delete()
        db.session.commit()
        creatoralbum.query.filter_by(id=albumid).delete()
        db.session.commit()
        return redirect(url_for('creator_home' , userid = userid))


@app.route('/album/deletesong/<userid>/<albumid>/<songid>',methods=[ 'GET'])
def deletesongfromalbum(userid, albumid , songid):
    user1 = user.query.filter_by(username=userid).first()
    if user1 == None:
        msg = f"No User Found Please Register"
        return msg
        # return render_template('login.html', message=msg)
    albumdetails.query.filter_by(albumid =albumid , songid = songid).delete()
    db.session.commit()
    return redirect(url_for('viewalbum', userid = userid , albumid = albumid))



@app.route('/album/addsong/<userid>/<albumid>',methods=['POST', 'GET'])
def addsongtoalbum(userid, albumid ):
    if request.method=='POST':
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
            # return render_template('login.html', message=msg)
            # return render_template('login.html', message=msg)
        songid = request.form.getlist('selected_songs')
        for xid in songid:
            albumdetails1 = albumdetails(
                albumid=albumid,
                songid=xid
            )
            db.session.add(albumdetails1)
        db.session.commit()
        return redirect(url_for('creator_home', userid=userid))
        return redirect(url_for('viewalbum', userid = userid , albumid = albumid))
    songss = []
    data = songs.query.filter_by(uploadedby = userid ).all()
    for son in data:
        availability = albumdetails.query.filter_by(songid = son.id , albumid = albumid).first()
        if availability is None:
            songss.append(son)
    return render_template('/creator/addsongstoalbum.html', userid = userid , songs = songss , albumid = albumid)







# -------------------- NORMAL USER ENDPOINTS--------------------------------------------




@app.route('/user/home/<int:page>/<userid>',methods=['GET'])
def user_home(userid, page):
    allsongs = songs.query.limit(page*4).all()
    allalbums = useralbum.query.filter_by(author = userid).all()
    geenres = genres.query.all()
    gens =[]
    ss =[]
    for g in geenres:
        song =  songs.query.filter_by(genre = g.genrename).order_by(songs.averagerating.desc()).first()
        if song:
            gens.append(g.genrename)
            ss.append(song)
    return render_template('/user/home.html', userid =userid , songs=allsongs  , albums=allalbums , genredata = zip(gens , ss) , page = page , message = None)

@app.route('/user/lyrics/<songid>/<userid>',methods=['GET'])
def viewuserlyrics(songid, userid):
    song = songs.query.filter_by(id=songid).first()
    if song:
        filename = song.filename
        lyrics = song.lyrics
        return render_template('/user/play.html',  lyrics = lyrics , filename = filename , userid =userid , songid = songid)
    return "No Existing song found"

@app.route('/user/about/<songid>/<userid>',methods=['GET','POST'])
def aboutsong(songid, userid):
    if request.method =='GET':
        song = songs.query.filter_by(id=songid).first()
        if song:
            return render_template('/user/about.html',  song = song, userid =userid , songid = songid)
        return "No Existing song found"
    rating = int(request.form['rating'])
    rating1 = ratings(songid = songid,
                      ratedby = userid,
                      ratingvalue = rating,
                      )
    song = songs.query.filter_by(id=songid).first()
    prevtot = round(song.averagerating * song.ratingcount)
    prevtot += rating
    song.ratingcount  = song.ratingcount+1
    prevtot/= song.ratingcount
    song.averagerating = round(prevtot,2)
    db.session.commit()
    db.session.add(rating1)
    db.session.commit()
    return redirect(url_for('user_home' , userid = userid , page =1))



@app.route('/user/createalbum/<userid>',methods=['POST', 'GET'])
def createalbumuser(userid):
    if request.method == 'POST':
        albumname = request.form['albumname']
        author = userid
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
        useralbum1 = useralbum(
            author =author,
            album_name = albumname
        )
        db.session.add(useralbum1)
        db.session.commit()
        albumid = useralbum1.id
        songid =request.form.getlist('selected_songs')
        for xid in songid:
            albumdetails1 = useralbumdetails(
                albumid=albumid,
                songid=xid
            )
            db.session.add(albumdetails1)
        db.session.commit()
        return redirect(url_for('user_home' , userid = userid , page =1))
    song = songs.query.all()
    return  render_template('/user/createalbum.html' , songs = song, userid = userid)



@app.route('/user/viewalbum/<userid>/<albumid>',methods=['GET'])
def viewuseralbum(userid, albumid):
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
        album = useralbum.query.filter_by(id =albumid ).first()
        if album==None:
            msg = f"No Album found Please Create One "
            return msg
        albumdetail = useralbumdetails.query.filter_by(albumid = albumid).all()
        songss =[]
        for item in albumdetail:
            song = songs.query.filter_by(id = item.songid).first()
            if song:
                songss.append(song)
        return render_template('/user/viewalbum.html' , userid = userid  , songs = songss , albumname =album.album_name , albumid = albumid )


@app.route('/user/addsongtoalbum/<userid>/<albumid>',methods=['POST', 'GET'])
def addsongtouseralbum(userid, albumid ):
    if request.method=='POST':
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
            # return render_template('login.html', message=msg)
            # return render_template('login.html', message=msg)
        songid = request.form.getlist('selected_songs')
        for xid in songid:
            albumdetails1 = useralbumdetails(
                albumid=albumid,
                songid=xid
            )
            db.session.add(albumdetails1)
        db.session.commit()
        return redirect(url_for('viewuseralbum', userid=userid, albumid = albumid))
    songss = []
    data = songs.query.all()
    for son in data:
        availability = useralbumdetails.query.filter_by(songid = son.id , albumid = albumid).first()
        if availability is None:
            songss.append(son)
    return render_template('/user/addsongstoalbum.html', userid = userid , songs = songss , albumid = albumid)


@app.route('/user/deletesong/<userid>/<albumid>/<songid>',methods=[ 'GET'])
def deletesonguseralbum(userid, albumid , songid):
    user1 = user.query.filter_by(username=userid).first()
    if user1 == None:
        msg = f"No User Found Please Register"
        return msg
        # return render_template('login.html', message=msg)
    useralbumdetails.query.filter_by(albumid =albumid , songid = songid).delete()
    db.session.commit()
    return redirect(url_for('viewuseralbum', userid = userid , albumid = albumid))




@app.route('/user/deletealbum/<userid>/<albumid>',methods=['GET'])
def deleteuseralbum(userid, albumid):
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg

        album = useralbum.query.filter_by(id =albumid )
        if album==None:
            msg = f"No Album found Please Create One "
            return msg
        useralbumdetails.query.filter_by(albumid=albumid).delete()
        db.session.commit()
        useralbum.query.filter_by(id=albumid).delete()
        db.session.commit()
        return redirect(url_for('user_home' , userid = userid , page = 1 ))


@app.route('/user/profile/<userid>/',methods=['GET'])
def userprofile(userid):
        user1 = user.query.filter_by(username=userid).first()
        if user1 == None:
            msg = f"No User Found Please Register"
            return msg
        return render_template('/user/profile.html' , userid = userid , user= user1 )


@app.route('/user/search/<userid>/',methods=['POST'])
def search(userid):
    keyword = request.form['query']
    namematched = songs.query.filter(songs.songname.contains(keyword) ).all()
    singermatched = songs.query.filter(songs.singer.contains(keyword) ).all()
    playlistsmatched = useralbum.query.filter(useralbum.album_name.contains(keyword)).all()
    return render_template('/user/search.html' , userid = userid , name = namematched , singer = singermatched , play = playlistsmatched, keyword = keyword)




#  ---------------------------------------------- ADMIN ROUTES -----------------------------------------

@app.route('/admin/register',methods=['POST', 'GET'])
def admin_register():
    if request.method =='POST':
        name =request.form['name']
        userid = request.form['userid']
        email = request.form['email']
        password = request.form['password']
        if (name ==None or userid ==None or email ==None or password ==None   ):
            msg = f"You can not leave a field empty"
            return render_template('/admin/register.html' , message=msg)
        condition = admin.query.filter_by(username=userid).first()
        if condition:
            msg = f"User Already Exists"
            return render_template('/admin/register.html', message=msg)

        new_user = admin(
            name=name,
            username=userid,
            email=email,
            password=password,
        )
        db.session.add(new_user)
        db.session.commit()
        return ("You have successfully registered ")
    return render_template('/admin/register.html' , message =None)


@app.route('/admin/login',methods=['POST', 'GET'])
def admin_login():
    if request.method =='POST':
        userid = request.form['userid']
        password = request.form['password']
        user1 = admin.query.filter_by(username=userid).first()
        if user1 ==None:
            msg = f"No User Found Please Register"
            return render_template('/admin/login.html', message=msg)
        if password != user1.password:
            msg = f"Incorrect Password! Try Again"
            return render_template('/admin/login.html', message=msg)
        return redirect(url_for('admin_home', userid =userid ))
    return render_template('/admin/login.html' , message =None)


@app.route('/admin/home/<userid>',methods=[ 'GET'])
def admin_home(userid):
    normal = user.query.count()
    creator = songs.query.distinct(songs.uploadedby).count()
    tracks = songs.query.count()
    albums = creatoralbum.query.count()
    genre = genres.query.count()
    popularsong = songs.query.order_by(songs.averagerating.desc).first()
    data = {
        'normal' : normal,
        'creator':creator,
        'tracks':tracks,
        'albums':albums,
        'genre':genre,
        'popularsong':popularsong

    }
    render_template('/admin/home.html' , data = data )