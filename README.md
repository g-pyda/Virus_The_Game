# Virus – The Game

**Virus – The Game** is a digital adaptation of a fast-paced, competitive card game focused on strategy, interaction, and controlled chaos. The game combines simple rules with high player interaction, making every match dynamic and unpredictable.

---

## How to Play

Panic has broken out at the hospital in *Leśna Dziura*. Laboratory staff have discovered that virus sample containers are empty. Experimental virus cultures have escaped and spread throughout the building — and now only you can stop them.

Your mission is to face the epidemic and compete to be the first to neutralize the viruses, saving the world from a full-scale pandemic. Players must build a human body while simultaneously defending it from infection, destruction, or organ theft carried out by infected opponents.

Prepare for battle. Gather your strength, plan your strategy, and do whatever it takes to win — all moves are allowed.

---

## Express Rules

- On your turn, either **play 1 card** or **exchange 1 to 3 cards**.
- Collect organs, protect them with vaccines, infect opponents’ organs with viruses, and use therapy cards.
- The first player to collect **4 healthy organs** wins the game.

---

## Why Play?

- A highly entertaining card game for players of all ages.
- Over **500,000 copies sold worldwide**.
- A true *“one more game”* experience.
- Perfect for travel, breaks, or holidays.

**Virus!** — the most contagious card game in the world, now recreated with modern digital technologies.

---

## Technologies Used

### Backend
- **Python** – core game logic and server-side processing.
- **WebSockets** – real-time communication between players.
- **API layer** – synchronization of game state and sessions.

### Frontend
- **HTML5 / CSS3 / JavaScript** – user interface.
- **Canvas-based rendering** – real-time gameplay visualization.
- **WebSocket client** – live interaction with the server.

### Infrastructure
- **Docker & Docker Compose** – containerized environment setup.
- **Environment variables (`.env`)** – configuration management.

---

## Initial Setup (Docker)

1. Ensure your firewall is switched off — otherwise the application will not connect through LAN.
2. Create a `.env` file based on `.env.example`.
3. Open a terminal and navigate to the `virus_the_game/` directory.
4. Run the following command:
   ```bash
   docker compose up
    ```
5. After startup, the main application will be accessible on all devices connected to the same LAN at:
  [http://{LAN_HOST_IP}:8000](http://{LAN_HOST_IP}:8000)
