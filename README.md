# nixtla

# What is OAuth

OAuth or Open Authorization is an authorization protocol that helps third-party application access to their resources without sharing their credentials but at the same time giving the necessary details to identify them.

Oauth works with the help of a token provided by the third-party application that can be used to get user details without entering a username or password.

A Client will send an authorization request to the resource owner or google in our case which in turn will grant us authorization. After sending the authorization grant to the Authorization server or google server it sends us an access token that can be used by the client to get protected resources such as username, id, and so on.

# How Does OAuth Code work

We generate a google client Id and a secret that can be used to use Google Oauth API. Just the code takes us to the normal public end point which displays a text.

/login creates auth url and tells oath.google the redirect url which is our auth url.

```
redirect_uri = request.url_for('auth')  # This creates the url for the /auth endpoint
```

The above line of code generates a redirect url.</br>

Here the user will be shown a set of his options email ids that he can use to login. The /auth url asks for the access token and sends it back to google to get the user details

```
access_token = await oauth.google.authorize_access_token(request)
```

the above line of code asks for the access token

/nixtla url takes this user object and displays the user name and an option to logout.

```
HTMLResponse(f'<p>Hello {name}!</p><a href=/logout>Logout</a>')
```

The above line of code displays the username that is extracted along with the logout option the redirects us to logout url

After clicking the logout option. The /logout will redirect you to the home page


# To run the image locally

To run Locally run the following command in the commnad terminal <br>
python run.py <br>

# TO Dockerize

 to build an image: docker build -t (image name) <br>
 to run an image in container:  docker run -d --name (container name) -p 80:80 (image_name)
