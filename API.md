# Authentication

## login

request POST /auth/login {

username : "email",

password : "pass"

}

response : {

token : "token"

}

## register

TBD

## change password

TBD

# Posts

## post new

request POST /post/new {

user_token : "",

post: {

    brand : "",

    type : "",

    amount : "",

    review : {},

    picture : "",

    pub_id : ""

    }

}

## load friend's posts

## load my posts
