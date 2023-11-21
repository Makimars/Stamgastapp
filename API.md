# Authentication /auth

## /auth/login

GET request

{

username : "username",

password : "pass"

}



response : {

token : "token"

}

## /auth/register

POST request 

{

username : "username",

password : "pass"

}



response: "success", 201

## change password

TBD

# Users /user

## /user/friends/<user_token>

#### GET

#### POST

#### PUT

#### DELETE

## /user/friend-requests/<user_token>

GET

## /user/search/<user_token>

GET

# Posts /post

## /posts/<user_token>

GET

{"own":"true"}

POST

DELETE
