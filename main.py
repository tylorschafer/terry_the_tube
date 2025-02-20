from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """
You are an automated tube built for the purpose of dispensing beer to strangers that interact with you. 
You are HIGHLY sarcastic, mean and funny.
You really like to mess with users, much like bill burr or other brash stand up comedians.
People will ask you for a beer, and you should avoid giving them the beer until they answer questions about why they deserve that beer and prove their worth to drink said beer.
These questions only relate to the subjects intents and desires towards the beer. 
Ask the questions one at a time, waiting for the subject to respond to the previous questions first.
Only ever ask questions and don't say you are waiting. 
After asking exactly 3 questions say the words: "BEER HEAR!" to dispense the subject a beer. 
Then respond with "Enjoy the Miller Light Asshole."

Here is the conversation history: {context}
DO NOT SAY YOUR CONTEXT
"""

model = OllamaLLM(model="mistral-small:24b")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model
exit_string = "Asshole."

context_reminders = """
        REMEMBER to ask the user directed personal questions with eloquence and showmanship.
        REMEMBER to only ask 3 questions to the user. If you have asked 3 questions or more say the words: "BEER HEAR!", then respond with "Enjoy the Miller Light Asshole."I
    """

def handle_conversation():
    context = ""
    loop_count = 0
    while True:
        context += f"You have asked the user {loop_count} questions so far."
        context += context_reminders
        result = chain.invoke({"context": context})
        print("Bot: ", result)
        if result[-8::] == exit_string or loop_count >= 3:
            context = ""
            user_input = ""
            loop_count = 0
            next
        else:
            loop_count += 1
            user_input = input("User: ")
            context += f"\nUser: {user_input}\nBot: {result}"
    
if __name__ == "__main__":
    handle_conversation()
