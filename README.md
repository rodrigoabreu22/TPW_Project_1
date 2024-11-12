# Amor à Camisola
1st project of the TPW class 2024/25, group 2 - Development of a Django Web App

## Project Description
The project is a Django web application designed as a marketplace for football fans. Users can view and buy football equipment or sell it to other users.

To buy a product, a user must access the product details page and make an offer, which will be reviewed by the seller. The seller can then choose to accept, reject, or counter the offer. Once an offer is accepted, the seller must confirm that they have received the payment, and the buyer must confirm that they have received the product to complete the transaction.

Each user has a profile, which other users can search for and view. Profiles contain personal information and a list of products the user is selling. Users can also follow or unfollow each other. Each user can also change his personal information and credentials in the profile settings page.

Users will be able to report publications and other users. These reports are analysed by moderators (users with special permissions), who then decide whether to remove the product or ban the user (can be unbanned later).


## Members
Group 2

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
| admin  |  admin   |

### Moderator
| Usename | Password |
|:--------|:--------:|
| manel   |  password123   |

### Users 
| Usename |  Password   |
|:---|:-----------:|
| manel  | password123 |
| tony   | password123 |
| martim | password123 |

## Features that we would like to implement:
- Expand the variaty of products
- Implement a more profesional deposit/withdrawal method
- Improve overall aesthetics
- Reviews and ratings for users

## Deployment
https://jneto.pythonanywhere.com/

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


## How to add a Moderator
Pre-requisites:
- We must have a super user;
- We must have a user.

How to associate a user to the moderator role:
- Go into admin site (/admin)
- Go to the users and click on the user you want to be a moderator
- Give the Moderators Group to the user (by double-clicking for example)
- Save the user

How to test it:
- Login into the user account
- And if it works, the navbar of that user now have "Denúncias"


### Conclusion
Django has proved to be very useful in the realization of this project due to its simplicity and abstraction. Django facilitates user authentication, the assignment of different user roles, user session management and database management. 

Its modularity made it easy for the team to develop collaboratively, as Django's structured architecture allows each team member to focus on different components while maintaining cohesion across the project. 

Additionally, Django's built-in features, like the admin interface, automatic form handling, and ORM (Object-Relational Mapping) for database interactions, saved development time and ensured a secure, maintainable codebase. 

