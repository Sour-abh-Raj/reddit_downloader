import random
import socket
import sys
import praw
import webbrowser

 
def receive_connection():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080)) # Change this according to your redirected url
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client
 
 
def send_message(client, message):
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()
 
 
def main():
    client_id = input(
        "Enter the client ID, it's the line just under Personal use script at the top: "
    )
    client_secret = input("Enter the client secret, it's the line next to secret: ")
    commaScopes = input(
        "Now enter a comma separated list of scopes, or all for all tokens: "
    )
  
    if commaScopes.lower() == "all":
        scopes = ["*"]
    else:
        scopes = commaScopes.strip().split(",")
 
    reddit = praw.Reddit(
        client_id=client_id.strip(),
        client_secret=client_secret.strip(),
        redirect_uri="YOUR_REDIRECT_URL",
        user_agent="YOUR_USER_AGENT",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes=scopes, state=state, duration="permanent")
    webbrowser.open(url)
    print(f"If the browser didn't open, open this url in your browser: {url}")
    sys.stdout.flush()
 
    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }
 
    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1
 
    refresh_token = reddit.auth.authorize(params["code"])
    send_message(client, f"Refresh token: {refresh_token}")
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())