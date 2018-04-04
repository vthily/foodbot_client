import uuid, os
from datetime import datetime
from pytz import timezone
from sqlalchemy.orm import sessionmaker
import base64
import pprint

from flask import Flask, render_template, flash, request, session, redirect, url_for
# testing the authentication
from functools import wraps
from flask import request, Response

from apiai_connector import ask_question_v2, ask_question
#from resources.tabledef_users import create_engine, User
from mlogging.mlogger import logger

from webUI_utilities import ChatForm
from webUI_utilities import suggest_commplete, format_response_list_with_links, format_response_text_with_links

# Support the audio/wav files
import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
# End of support the audio/wav files

#engine = create_engine('sqlite:///resources/users.db', echo=True)
CUR_DIR = os.path.dirname(os.path.realpath(__file__))
intents_db = os.path.join(CUR_DIR, 'resources/all_intents.json')

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'

# Support the audio/wav files
UPLOAD_FOLDER = os.path.join(CUR_DIR, 'audio_input/uploads')
WAVS_FOLDER = os.path.join(CUR_DIR, 'audio_input/direct')
ALLOWED_EXTENSIONS = set(['wav', 'mp3'])
__DEBUG__ = True

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# End of support the audio/wav files


# Support the audio/wav files - checking the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# testing the authentication
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
# end of testing the authentication

@app.errorhandler(404)
def page_not_found(e):
    return render_template('nsfnb_404.html'), 404  # Not Found


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('nsfnb_500.html'), 500  # Internal Server Error


@app.route("/chat")
#@requires_auth
def main_render():
    form = ChatForm(request.form)
    # ---------To clear the log each time the page is refreshed, even the same session id ----------#
    form.ssid = uuid.uuid4().hex
    if (form.ssid in form.chats.keys()):
        del form.chats[form.ssid][:]
    logger("webUI").info("You are requesting a new session by refresh: " + form.ssid)

    # ---------To keep log each time the page is refreshed but the time in bot response is lost ----------#
    logger("webUI").info("======================CHAT HISTORY======================")
    logger("webUI").info(form.chats)
    if len(form.chats.keys()) == 1:
        form.ssid = form.chats.keys()[0]
    logger("webUI").info("======================SESSION ID======================")
    logger("webUI").info(form.ssid)
    if (__DEBUG__):
        print ("Session id: " + str(form.ssid))

    retro_msg = [{"text": "Welcome! I am North-Spine Food Ordering bot."}]
    retro_details = [[{'text': 'Ordering food in canteen A (NorthSpine)', 'link': 'http://www.ntu.edu.sg/has/FnB/Pages/NorthSpine.aspx'}],
                     [{'text': 'Getting to know the location of Canteen A', 'link': 'http://maps.ntu.edu.sg/m?q=Canteen%20A&fs=m'}]
                    ]
    link = []
    singaporetz = timezone('Asia/Singapore')
    form.chats[form.ssid] = []
    form.chats[form.ssid].insert(0, {
                      #'user':  ("User: Get started"),
                      'bot': (retro_details),
                      'retro': (retro_msg),
                      'link': (link),
                      'time': datetime.now(singaporetz),
                      'id': len(form.chats[form.ssid]) + 1,
                      'feedback': ''
                      })

    return render_template('nsfnb_chat.html', form=form)


@app.route("/upload", methods=['POST', 'GET'])
def receive_wav_files():
    form  = request.form
    if (request.method == 'POST'):
        # UPLOAD_FOLDER
        #print (request.form)
        split_ind = request.form['data'].find(",")

        data = request.form['data'][(split_ind + 1):]
        decodedData = base64.decodestring(data)

        filename = (request.form['fname']).replace("%3A", ":")
        #print ("The output filename is " + filename)
        #print (decodedData)
        with open(WAVS_FOLDER + "/" + filename, 'wb') as wavfile:
            wavfile.write(decodedData)

        logger("voice_input").info("The output file is " + UPLOAD_FOLDER + "/" + filename)

    return render_template('nsfnb_chat.html', form=form)


from datetime import datetime
@app.route("/chat", methods=['POST', 'GET'])
def receive_query():
    form = ChatForm(request.form)

    # Select to use session id info (1. generated from client, or 2. returned from dialogflow|api.ai)
    if (request.form['session_id'] == ''):
        form.ssid = uuid.uuid4().hex
    else:
        form.ssid =request.form['session_id']
    # If the ssid is new, should clear the chat log - history.
    if (form.ssid not in form.chats.keys()):
        form.chats[form.ssid] = []

    last_ind = len(form.chats[form.ssid])
    if (last_ind > 0):
        logger("webUI").info("Last query, response and feedback: ")
        logger("webUI").info(form.chats[form.ssid][0])

    singaporetz = timezone('Asia/Singapore')
    user_query = ""
    timestamp_userquery = datetime.now(singaporetz)

    """
    #CHECK IF THE INPUT IS AUDIO -> CONVERT TO TEXT THEN ASSIGN TO USER_QUERY
    logger("webUI").info("UPLOAD FILE debugging - start")
    if (request.method == 'POST'):
        # check if the post request has the file part
        if 'au_file' not in request.files:
            flash('Warning: No file part')
            return redirect(request.url)
        file = request.files['au_file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('Warning: No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            logger("webUI").info("UPLOAD FILE debugging - end")
            return redirect(url_for('receive_query', _external="true", _scheme="https"))
    """

    # Get information returned form dialogflow (FAQs agent)
    user_query = request.form['user_query']
    if (__DEBUG__):
        print ("1. Your query is ")
        pprint.pprint(user_query)

    if (user_query.strip() != ""):
        #(bot_response, detail_list, links, sessionid, timestamp_insgtz, intentname, params) = ask_question(user_query)
        (bot_response, detail_list, links, sessionid, timestamp_insgtz, intentname, params) = ask_question_v2(user_query)
        if (__DEBUG__):
            print ("---------------------------")
            pprint.pprint(params)
            print ("---------------------------")

        # Delete the chat history if the ssid is different.
        logger("webUI").info("Return session from api.ai: " + sessionid)
        if not (sessionid in form.recent_sessionids):
            form.recent_sessionids.append(sessionid)
            del form.chats[form.ssid][:]

        # update the form's parameters from result.
        form.intent_name = intentname
        form.intent_params = params
        form.timestamp = timestamp_insgtz

        formated_details = format_response_list_with_links(detail_list, links)
        formated_retro_response = format_response_text_with_links(bot_response, links)

        if (__DEBUG__):
            print ("2. Inserting data to forms.chats")
        #form.chats[form.ssid].insert(0, {
        #                      'user':  ["User (" + str(timestamp_userquery) + ")",  user_query],
        #                      'bot': (formated_details),
        #                      'retro': (formated_retro_response),
        #                      'link': (links.values()),
        #                      'time': form.timestamp,
        #                      'id': len(form.chats[form.ssid]) + 1,
        #                      'feedback': ''
        #                      })

        form.chats[form.ssid].append({
                              'user':  ["User (" + str(timestamp_userquery) + ")", user_query],
                              'bot': (formated_details),
                              'retro': (formated_retro_response),
                              'link': (links.values()),
                              'time': form.timestamp,
                              'id': len(form.chats[form.ssid]) + 1,
                              'feedback': '',
                              'meta': params,
                              })

        if (__DEBUG__):
            print ("3. Number of elements: " + str(len(form.chats)))

        form.similar_queries = suggest_commplete(user_query)
    return render_template('nsfnb_chat.html', form=form)


@app.route('/login', methods=['POST'])
def do_admin_login():
    POST_USERNAME = str(request.form['username'])
    POST_PASSWORD = str(request.form['password'])

    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        #return "Hello Boss!  <a href='/chat'>Go to chat page</a>"
        return redirect(url_for("receive_query"))


if __name__ == "__main__":
    cwd = os.getcwd()
    os.environ["PYTHONPATH"] = cwd
    app.run(host='0.0.0.0', port=4010)
