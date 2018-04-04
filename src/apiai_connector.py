# -*- coding: utf-8 -*-

import os, sys, re
import json
import apiai
import uuid

from mlogging.mlogger import logger
from datetime import datetime
from pytz import timezone
from dateutil import tz


CLIENT_ACCESS_TOKEN = 'YOUR_AGENT_ACCESS_TOKEN' 
session_id = uuid.uuid4().hex
__DEBUG__ = True

"""
url matching regex
http://daringfireball.net/2010/07/improved_regex_for_matching_urls
https://gist.github.com/gruber/8891611
"""
ANY_URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""

"""
The regex patterns in this gist are intended only to match web URLs
match all URLs, regardless of protocol, see: https://gist.github.com/gruber/249502
"""
WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""

"""
This regex pattern matches IP:PORT
"""
IP_REGEX = r"""[0-9]+(?:\.[0-9]+){3}:[0-9]+"""

def separate_retro_with_detail(text_response_wolink):
    split_ind = len(text_response_wolink)

    # The intro response should be first sentences until the first <section> tag
    if ('<section>' in text_response_wolink):
        split_ind = text_response_wolink.index('<section>')
    elif ('<li>' in text_response_wolink):
        split_ind = text_response_wolink.index('<li>')

    intro_response = text_response_wolink[:(split_ind)].strip()
    detail_response = text_response_wolink[(split_ind):]
    return (intro_response, detail_response)


def format_response(text_response):
    text_response_wo_link = text_response
    retlinks = {}

    # @description: This part is to detect and extract all links in the response (It could be returned from dialogflow or web-hook
    # @input: Text response
    # @output: dictionary of link with {link<1|2|...|n>: http address}
    logger("chat").info("4.1. Extract links from the response")
    if ("http" in text_response):
        links = re.findall(WEB_URL_REGEX, text_response)
        i = 1
        for url in links:
            if not(url.startswith('http')):
                continue
            text_response_wo_link = text_response_wo_link.replace(url, 'link' + str(i))
            retlinks['link' + str(i)] = url
            i = i + 1
            logger("chat").debug("     -> Detecting link " + url)

    (intro_response, detail_response) = separate_retro_with_detail(text_response_wo_link)
    logger("chat").info("4.2. Extract retro/introduction from response: " + intro_response)

    # Split detail into list and remove the empty elements.
    # To ignore the case where empty or element with 'spaces', need to check detail_response start with '-' or not first.
    # Ignore the new line in the text, to prevent to mismatch of regular expression later in the code.
    responses = []
    formated_responses = []
    if not (detail_response == ""):
        detail_response = detail_response.replace("\n", " ")
        detail_response = detail_response.replace("<section>", "<li><section>")

        responses = filter(None, detail_response.split("<li>"))
        for response in responses:
            if response.strip() == '':
                continue
            else:
                formated_responses.append(response.strip())

    # Return: retro text, list of detail response, dictionary of links
    logger("chat").info("4.3. Format the details/list from response: ")
    logger("chat").info("     -> ".join(formated_responses))
    return (intro_response, formated_responses, retlinks)


def is_reset_context_request(inputquery):
    if (("skip" or "cancel" or "ignore" or "move on" or "clear" or "reset") in inputquery.lower()):
        return True
    return False


def convert_my_iso_8601(iso_8601, tz_info):
    assert iso_8601[-1] == 'Z'
    iso_8601 = iso_8601[:-1] + '000'
    iso_8601_dt = datetime.strptime(iso_8601, '%Y-%m-%dT%H:%M:%S.%f')
    return iso_8601_dt.replace(tzinfo=timezone('UTC')).astimezone(tz_info)

import pprint
def ask_question_v2(input_query):
    global session_id

    # Initiate the Dialogflow agent
    logger("chat").info("Receiving input query" + input_query)
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
    request = ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'
    request.session_id = session_id
    request.query = input_query.replace("\"", "'")
    request.resetContexts = is_reset_context_request(input_query)

    logger("chat").info("Request sent to YakunFood Agent")
    logger("chat").info(request)

    # Get the response from dialogflow agent
    response = request.getresponse()
    responsestr = response.read().decode('utf-8')
    response_obj = json.loads(responsestr)
    logger("chat").info("Receiving response from api.ai agent" + responsestr)

    text_response = response_obj["result"]["fulfillment"]["speech"]
    logger("chat").info("Response to display in webpage: " + text_response)

    return_session_id = response_obj["sessionId"]
    rich_messages = {"text": [], "quickreplies": [], "cards": []}

    detail_msgs = response_obj["result"]["fulfillment"]["messages"]
    for resp_message in detail_msgs:
        msg_type = (resp_message['type'])
        if (msg_type == 0):
            rich_messages["text"] = rich_messages["text"] + format_text_on_website(resp_message)
            if (__DEBUG__):
                print("Format of text on website:")
                pprint.pprint(rich_messages["text"])
        elif (msg_type == 1):
            # Processing the button/card
            rich_messages["cards"] = rich_messages["cards"] + format_cards_on_website(resp_message)
            if (__DEBUG__):
                print("Format of cards on website:")
                pprint.pprint(rich_messages["cards"])
        elif (msg_type == 2):
            # Processing the quickReplies
            rich_messages["quickreplies"] = rich_messages["quickreplies"] + format_quickreplies_on_website(resp_message)
            if (__DEBUG__):
                print("Format of quickreplies on website:")
                pprint.pprint(rich_messages["quickreplies"])
        else:
            # Processing the carousell?
            pass

    # PROCESS THE RESPONSE - FORMAT
    (intro_response, detail_responses, links) = format_response(text_response)
    intent_name = ""
    if ("intentName" in  (response_obj["result"]["metadata"]).keys()):
        # In case there is no intent name: using smalltalk or other pre-built agents from dialogflow| api.ai| google
        intent_name = response_obj["result"]["metadata"]["intentName"]
        if (intent_name == "Default Fallback Intent"):
            # If the agent cannot recognize the intent, we will suggest user topics of their queries.
            intro_response = "You can ask me something related to ordering food and beverage in Canteen A (North Spine, NTU, Singapore)."
            detail_responses = []

    # If no intent name (small talk or prebuilt agents), using the action name instead.
    actionname = response_obj["result"]["action"]
    if (intent_name == ""):
        intent_name = actionname

    # Return the parameters, this is for debugging.
    parameters = dict(response_obj["result"]["parameters"])
    response_timestamp = response_obj["timestamp"]

    # Convert time zone
    singaporetz = timezone('Asia/Singapore')
    timestamp_insgtz = convert_my_iso_8601(response_timestamp, singaporetz)

    return (intro_response, detail_responses, links, return_session_id, timestamp_insgtz, intent_name, rich_messages)


def format_quickreplies_on_website(qR_data):
    qR_responses = []
    if (type(qR_data) != type({})):
        return qR_responses

    qR_responses.append(qR_data['title'])
    qR_responses = qR_responses + qR_data['replies']
    return qR_responses

import pprint
def format_text_on_website(text_data):
    text_msg = []
    if type(text_data["speech"]) == type([]):
        text_msg = text_data["speech"]
    else:
        text_msg.append(text_data["speech"])
    return text_msg

def format_cards_on_website(card_data):
    img_responses = []
    if (type(card_data) != type({})):
        return img_responses

    img_responses.append(card_data['title'])
    img_responses.append(card_data['imageUrl'])
    return img_responses


def format_other_info_on_website(other_data):
    pass
