"""
Project Title: Password Generator & Manager

Description: This is a Console-Based Project on Password Generator and Manager which is developed using Core Python concepts.
This will allow users to store and manage their passwords securely for different websites and applications.

Features:
- Generate strong random passwords
- Create new credentials (site,username,password)
- Read stored credentials
- Update existing credentials
- Delete credentials
- Password strength checking (Weak/Strong)
- File Handling for permanent data storage

Technologies used:
- Core Python
- Loops and Conditional Statements
- Functions
- Dictionary
- File Handling
- Modules
- String methods

Objective:
The main objective of this project was to understand and use Core Python concepts
to build a application that generates and manages passwords securely and safely.

Scope of the Project:
- Works in terminal
- Stores data in a text file
- Console-Based application

Conclusion:
This project shows the use of Core Python programming concepts like loops,conditional statements,
file handling, to build a simple and effective password generator and manager system.

"""

import random
import string

def check_strength(password):
    if len(password) < 8:
        print("Weak Password (minimum 8 characters required)")
    else:
        print("Strong Password")

def mask_password(password):
    return "*" * len(password)

credentials = {}

def generate_password():
    length = int(input("Enter password length: "))
    characters = string.ascii_lowercase + string.digits + "@"
    password = "@"

    for i in range(length - 1):
        password += random.choice(characters)
    print("Generated Password: ", mask_password(password))
    show = input("Do you want to see the password? (Y/N):")

    if show.upper() == "Y":
        print("Actual Password:", password)
    check_strength(password)

def add_credential():
    site = input("Enter your site name: ")
    username = input("Enter your username: ")
    password = input("Enter your password (you can use @ or _): ")

    print("Your Password:", mask_password(password))

    show = input("Do you want to see the password? (Y/N):")

    if show.upper() == "Y":
        print("Actual Password:", password)
    check_strength(password)

    credentials[site] = (username,password)

    with open("data.txt","a") as file:
        file.write(site + "," + username + "," + password + "\n")

    print("Credentials saved successfully!")

def read_credentials():
    try:
        with open("data.txt","r") as file:
            data = file.readlines()
        if len(data) == 0:
           print("Sorry!, Credentials Not Found")
        else:
            for line in data:
                site,username,password = line.strip().split(",")
                print("Site: ",site, "| Username: ",username, "| Password: ",password)

    except FileNotFoundError:
        print("Sorry! File Not Found!")

def update_credential():
    site_to_update = input("Enter the name of the site to update: ")
    new_username = input("Enter your new username: ")
    new_password = input("Enter you new password: ")
    print("Your Password:",mask_password(new_password))

    show = input("Do you want to see the password? (Y/N):")

    if show.upper() == "Y":
        print("Actual Password:", new_password)
    try:
        with open("data.txt","r") as file:
            data = file.readlines()
        updated = False

        with open("data.txt","w") as file:
            for line in data:
                site,username,password = line.strip().split(",")

                if site == site_to_update:
                    new_username = input("Enter your new username: ")
                    new_password = input("Enter your new password: ")

                    check_strength(new_password)

                    file.write(f"{site},{new_username},{new_password}\n")
                    updated = True
                else:
                    file.write(line)
        if updated:
            print("Congratulations!, Credentials Updated Successfully!")
        else:
            print("Sorry!,Try Again!")
    except FileNotFoundError:
        print("Sorry!, File Not Found!")

def delete_credential():
    site_to_delete = input("Enter the name of the site to delete: ")

    try:
        with open("data.txt","r") as file:
            data = file.readlines()
        deleted = False

        with open("data.txt","w") as file:
            for line in data:
                site,username,password = line.strip().split(",")

                if site == site_to_delete:
                    deleted = True
                    continue
                else:
                    file.write(line)
        if deleted:
            print("Credentials Deleted Successfully!")
        else:
            print("Sorry!, Site Not Found!")

    except FileNotFoundError:
        print("Sorry!, File Not Found!")

while True:
   print("-----Password Generator & Manager-----")
   print("1.Generate Password")
   print("2.Create new Password")
   print("3.Read Credentials")
   print("4.Update Password")
   print("5.Delete Password")
   print("6.Exit")

   option = input("Enter number of the option: ")

   if option == "1":
       generate_password()

   elif option == "2":
       add_credential()

   elif option == "3":
       read_credentials()

   elif option == "4":
       update_credential()

   elif option == "5":
       delete_credential()

   elif option == "6":
       print("Exiting from program.....")
       break
   else:
       print("Invalid option")