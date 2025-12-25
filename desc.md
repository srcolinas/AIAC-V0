# Teyuna

Here is implemented a game called Teyuna. It is inspired by Settlers of Catan, but not exactly it. It is focused around the Tayoronas, an indigineous group from a region that today is called Sierra Nevada de Santa Marta, in Colombia. 


## Features

1. Users can authenticate through username and passwords.
2. The game can be played by either humans (through the web browser client) and LLM based AI agents (through a terminal base AI client).
3. Once a user logs in into the application, they can either start a new game (which generates a unique token to identify it) or join an existing game by pasting an existing token in a text box.
4. A game can only start with either 3 or 4 players, which is decided by the player who initiated the game. 
5. The backend has a public facing API, which is used by both the web brower and AI agent client. 


## Tech Stack

1. The backend is written in Python using FastAPI.
2. The frontend is written in React.
3. The AI client is written in Python using Pydantic AI.
4. The databased used to keep track of game, users and leaderboard is Postgresql.