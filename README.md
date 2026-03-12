# weekend-planner-python
CLI-based Python travel planner featuring MySQL user profiles, bookmark management, and a categorized database of 100+ locations.

# Weekend Planner (Python Project)

Weekend Planner is a Python-based travel planning application designed to help users explore and organize weekend destinations in Kolkata. The program allows users to browse categorized locations, manage personal profiles, bookmark places, and provide feedback through a structured menu-driven interface.

## Features

- User profile system with authentication (MySQL database)
- Bookmark system for saving preferred locations
- Anonymous feedback submission
- Admin dashboard for reviewing suggestions and profiles
- Random location generator for discovering new places
- Menu-driven GUI-style terminal interface
- Detailed location database with 100+ curated places

## Location Categories

The application includes categorized destinations such as:

- Entertainment (cinemas, arcades, amusement parks, bowling alleys)
- Cultural and educational attractions (museums, historical sites, science centres)
- Recreational places (zoos, botanical gardens, leisure parks, spas)
- Food and drink establishments (cafes, bakeries, bars, pubs)
- Shopping malls and commercial centres

Each location includes detailed metadata such as:

- Address
- Timings
- Ratings
- Amenities
- Contact information
- Pros and cons
- Pricing information

## Technologies Used

- Python
- MySQL database
- Binary file storage (pickle)
- CSV configuration files
- Structured menu-based CLI interface

## Data Architecture

Location data is stored in a binary file (`Places.dat`) using lists of dictionaries.  
User data is stored in a MySQL database containing:

- Username
- Password
- Bookmarks
- Feedback
- Profile timestamps

The program uses a token-based navigation system that maps user input to program functions for efficient menu transitions.

## Key Functional Modules

- Database initialization and connection management
- User profile creation and authentication
- Bookmark management
- Feedback handling
- Admin profile management
- Location browsing and detailed information display

## Dataset

The application contains a curated dataset of **100+ locations in Kolkata**, including entertainment venues, cultural attractions, restaurants, and shopping centres.

## Purpose

This project was developed as a **Class XII Computer Science final project**, demonstrating concepts such as:

- File handling
- Database integration
- Data structures
- Modular programming
- Error handling
- User authentication systems
