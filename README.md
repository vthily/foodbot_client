# foodbot_client
This is the web interface of the dialogflow v2 agent. You have to build the agent with Dialogflow v2 first, then this project is the interface via web page, to have a conversation with this agent.

  - Ubuntu 14.x   
  - Python 2.7

More about the dialogflow framework here: https://dialogflow.com/

# What can you do with this web interface?
- Send user queries by enter text or voice (Google Voice, SingaporeEnglish).
- Rich messages in response: text, image, quick replies.
- Ask and order food, drinks, and how to purchase.


# Dependencies
List of packages required to install before running the client:

    pytz   
    python-dateutil   
    sqlalchemy   
    flask   
    apiai   
    pyenchant   
    wtforms   
    ntlk 
  

# Notes before running
1. Update the path to logs folder (in src/mlogging/logging.json, renaming logging_template.json to logging.json): should replace the actual path in your server (assume you clone the code to /local/foodchatbot/webUI), for example:


    sys_log_dir/verbose.log => /local/foodchatbot/webUI/logs/verbose.log    
    sys_log_dir/info.log => /local/foodchatbot/webUI/logs/info.log    
    sys_log_dir/errors.log => /local/foodchatbot/webUI/logs/errors.log


2. Update your client access token to your bot agent (src/apiai_connector.py)

    CLIENT_ACCESS_TOKEN = 'YOUR_AGENT_ACCESS_TOKEN' 


# Running the web interface
Go to src folder and running the command

    $ python webUI.py
  
    
Checkout the browser http://localhost:4010/chat and start chatting with your agent, or http://<your_ip_addr>:4010/chat
(The voice is not supported if you use the ip address). And the port number is reflected in your code in webUI.py

    app.run(host='0.0.0.0', port=4010)


