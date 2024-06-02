# Description

The project is created to solve event management problems. This represents a FastAPI + tg bot backend as a frontend. Available features: managing events, reminding them with a convenient calendar in the tg bot.

## Usage

1. Clone the repo
    ```sh
        git clone https://github.com/RAT-404/time_manager.git
    ```
2. Enter next params to `.env` file, it need to create in base directory, you need to use your arguments in this file ( exclude fields POSTGRES_HOST, REDIS_HOST and API_URL ):

    ```sh
       POSTGRES_DB=your_db_name
       POSTGRES_USER=your_db_user
       POSTGRES_PASSWORD=your_db_password
       POSTGRES_PORT=your_db_port
       POSTGRES_HOST=host.docker.internal

       REDIS_PORT=your_redis_db_port
       REDIS_HOST=host.docker.internal

       BOT_TOKEN=your_bot_token
       API_PORT=your_api_port
       API_URL=http://host.docker.internal:${API_PORT}/event/
    ```

3. To start with docker from base project directory:
    ```sh
    docker-compose up --build
    ```
4. Go to your bot in telegram and enter /all

    To start bot your need go to tg_bot directory and start command

## License

[MIT](https://choosealicense.com/licenses/mit/)
