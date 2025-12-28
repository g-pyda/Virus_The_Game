# Virus_The_Game

## Initial setup (Docker)

1. Ensure your firewall is switched off, the app will not connect through LAN otherwise!
2. In text editor of your choice, create a ```.env``` file, following the ```.env.example``` guidelines.
3. Open a terminal and ensure you are in the ```virus_the_game/``` directory.
4. Run the following docker command:

```bash
docker compose up
```

Now, the mother unit of the app is accessible on all the LAN connected devices on
[http://{LAN_HOST_IP}:8000](http://{LAN_HOST_IP}:8000)
