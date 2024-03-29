# Description

The project is created to solve event management problems. This represents a FastAPI + tg bot backend as a frontend. Available features: managing events, reminding them with a convenient calendar in the tg bot.

## Usage

1. Clone the repo
    ```sh
    git clone https://github.com/RAT-404/time_manager.git
    ```
2. Enter next params to `.env` file, it need to create in base directory:

    ```sh
       POSTGRES_DB=your_db_name
       POSTGRES_USER=your_db_user
       POSTGRES_PASSWORD=your_db_password
       POSTGRES_PORT=your_db_port
       POSTGRES_HOST=your_host_postgres_db

       REDIS_PORT=redis_db_port
       REDIS_HOST=your_host_redis_for_db

       BOT_TOKEN=your_bot_token

       API_URL=your_API_url
    ```

    For fields POSTGRES_HOST and REDIS_HOST:
    If you using app with docker, you should write host.docker.internal, else write your url.
    For fields API_URL:
    Check port in this url and dockerfile in backend directory ( default url can be http://localhost:8000/event or if you use docker http://host.docker.internal:8000/event ).

3. To start with docker from base project directory:
    ```sh
    docker-compose up --build
    ```
4. Or to start from cmd you need start main files from backend and tg_bot directories.

    ```sh
    uvicorn main:app --reload --port 8000
    ```

    To start backend your need go to backend directory and start command. It start API with uvicorn on 8000 port.

    ```sh
    python main.py
    ```

    To start bot your need go to tg_bot directory and start command

## License

[MIT](https://choosealicense.com/licenses/mit/)
