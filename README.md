# Amor à Camisola

## Project Description
The project consists of a Django web application with the marketplace concept, dedicated to football fans. Users will be able to view and buy football equipment or sell it to other users. 

## Members

| Name | NMec |
|:---|:---:|
| Rodrigo Abreu | 113626 |
| João Neto | 113482 |
| Ricardo Antunes | 115243 |


## Functionalities

### Unauthenticated user:
- View products in the feed
- Filter the products in the feed
- View product details
- Search for a product
- View a user profile
- Search for a user
- Register
- Log in


### Authenticated user:
- All unauthenticaded user functionalities
- List a product for sale
- View offers on my products
- Accept, reject or counter an offer for a product
- Make an offer on a product
- Confirm an offer
- View my sales/purchase history
- Add a product to the favourites list
- Remove a product from the favourites list
- Deposit or withdraw money in my account
- View/edit my profile
- View other users' profile
- Follow/unfollow a user
- View my followers/following
- Report a user or product publication 
- Log out


### Moderator:
- All authenticated user functionalities
- Review reports 
- Delete publications 
- Ban users 


## User Accounts

### Admin
| Usename | Password |
|:--------|:--------:|
| admin   |  admin   |

### Users 
| Usename |  Password   |
|:---|:-----------:|
| manel  | password123 |
| tony   | password123 |
| martim | password123 |

## Features that we would like to implement:
- Possibility to remove my published products
- Expand the variaty of products
- Implement a more profesional deposit/withdrawal method
- Improve overall aesthetics
- Reviews and ratings for users

## Deployment
https://rantunes038.pythonanywhere.com/

## How to add a Moderator
Pre-requisites:
- We must have an admin;
- We must have a user.

How to associate a user to the moderator role:
- Go into admin site (/admin)
- Go to the users and click on the user you want to be a moderator
- Give the Moderators Group to the user (by double-clicking for example)
- Save the user

How to test it:
- Login into the user account
- And if it works, the navbar of that user now have "Denúncias"

## How to run it locally

If you have this files remove them:

    db.sqlite3
    migrations/<any file that is not __init__.py>

Commands to run the code:
```bash
    python3 manage.py makemigrations
    python3 manage.py migrate
    python3 insertData.py
    python3 manage.py runserver
```


