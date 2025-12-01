from flask import Flask, request
import requests
import os
from dotenv import load_dotenv


load_dotenv()


PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

app = Flask(__name__)

premiere_interaction = True



def analyser_intention(message, premiere_interaction):
    message = message.lower()
    
    if "salut" in message:  
        if premiere_interaction:  
            return "salutations"
        else:                    
            return "bye" 
    if "bonjour" in message or "allo" in message:
        return "salutations"
    if "patate" in message:
        return "patate"
    if "prix" in message:
        return "prix"
    if "pomme" in message:
        return "pomme"
    if "goodbye" in message or "a plus" in message or "a la prochaine" in message or "bye" in message:
        return "bye"
    return "inconnu"

def generer_reponse(intention):
    if intention == "salutations":
        return "Bonjour ! Ça va mon amour ?"
    if intention == "patate":
        return "C'est bon des patates."
    if intention == "prix":
        return "C'est 100$ pour me parler.\nC'est 50$ pour les meilleures photos:)"
    if intention == "pomme":
        return "C'est bon les pommes."
    if intention == "bye":
        return "Bye mon chou!"
    return "Je t'aime mon chou !"

def envoyer_message(id_destinataire, texte):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": id_destinataire},
        "message": {"text": texte}
    }
    requests.post(url, params=params, json=payload)


@app.route("/", methods=["GET"])
def verifier_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Erreur : token invalide", 403

@app.route("/", methods=["POST"])
def recevoir_message():
    global premiere_interaction

    data = request.get_json()

    if "entry" in data:
        for entry in data["entry"]:
            for event in entry["messaging"]:
                if "message" in event and "text" in event["message"]:
                    texte = event["message"]["text"]
                    sender_id = event["sender"]["id"]

                    intention = analyser_intention(texte, premiere_interaction)
                    reponse = generer_reponse(intention)
                    premiere_interaction = False

                    envoyer_message(sender_id, reponse)

    return "EVENT_RECEIVED", 200



if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
