'''
Created on 13 Nov 2017

@author: ly
'''
import enchant
import re, os

from wtforms import Form, TextField, validators, TextAreaField
from nltk.tokenize import MWETokenizer
from mlogging.mlogger import logger

CUR_DIR = os.path.dirname(os.path.realpath(__file__))


class ChatForm(Form):
    user_query = TextField(u'User query', validators=[validators.required()])       # User query (text format)
    bot_response = TextField(u'Bot response', validators=[validators.optional()])   # Text response from faq agent (api.ai) + webhook

    similar_queries = []    # Suggest correct typo questions, using pyenchant
    query_categories = []   # Classify the user query into different sub-topics. NOW HARD-CODED!
    recent_sessionids = []  # Saving all recently session ids (from different PCs, or different working sessions)
    recent_queries = []     # 10 recently queries from all users.
    chats = {}              # Chat history, with key is session id, value is the chat logs until session is timeout.

    ssid = ""               # Session id - assigned to each user.
    timestamp = ""          # To update information of bot response time information.
    intent_name = ""
    response_feedback = ""
    intent_params = dict()


def format_response_list_with_links(detail_list, links):
    logger("webUI").info(links.keys())
    new_details = []
    
    for detail in detail_list:
        m = re.match('(.*?)(link[0-9]+)', detail)
        item_detail = {}
        if bool(m):
            key = m.group(2)
            logger("webUI").info("Link index " + key + " and detail: " + detail)
            item_detail["text"] = detail.replace(key, "")
            if key in links.keys():
                item_detail["link"] = links[key]
                del links[key]
        else:
            item_detail["text"] = detail
            item_detail["link"] = ""
        
        new_details.append(item_detail)
    
    logger("webUI").info(new_details)
    return new_details


def format_response_text_with_links(text_reponse, links):
    if (len(links) == 0):
        return [{"text": text_reponse, "link": ""}]

    new_text_response = []
    matches = re.findall('((.*?)(link[0-9]+))', text_reponse)
    found_text = ""
    for match in matches:
        found_text = found_text + match[0]
        linkid = match[2]
        text_before_link = match[1]
        
        item_detail = {}
        item_detail["text"] = text_before_link
        if linkid in links.keys():
            logger("webUI").info("Link " + linkid + " after: " + text_before_link)
            item_detail["link"] = links[linkid]
            del links[linkid]
        
        new_text_response.append(item_detail)
    
    remain_text = text_reponse.replace(found_text, "").strip()
    if (remain_text != ""):
        new_text_response.append({"text": remain_text, "link": ""})
    
    logger("webUI").info(new_text_response)
    return new_text_response


def suggest_commplete(inSentence):
    suggestion_sentences = []
    
    tokenizer = MWETokenizer([('hors', "d'oeuvre"), ('program', 'me')], separator='+') # to define the words separated by spaces.
    personal_dictionary = os.path.abspath(os.path.join(CUR_DIR, 'resources', 'sg_words.txt'))
    d = enchant.DictWithPWL("en_US", personal_dictionary)
    
    new_sentence = inSentence
    meaning_words = tokenizer.tokenize(inSentence.split())
    
    for word in meaning_words:
        if (word in [".", "?", ","]):
            continue
        word = re.sub(r"[(),!?\'\`@-]", "", word)
        if (not d.check(word)):
            new_words = d.suggest(word)
            for new_word in new_words:
                new_sentence = inSentence.replace(word, new_word)
                suggestion_sentences.append(new_sentence)
    
    return suggestion_sentences

