# Description
The project is created to solve event management problems. This represents a FastAPI + tg bot backend as a frontend. Available features: managing events, reminding them with a convenient calendar in the tg bot.


# Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install time_manager.

```bash
pip install time_manager
```

## Usage

1. Clone the repo
   ```sh
   git clone https://github.com/RAT-404/time_manager.git
   ```
2. Enter next params to `.env` file, it need to create in base root
  POSTGRES_DB = your_db_name
  POSTGRES_USER = your_db_user
  POSTGRES_PASSWORD = your_db_password
  POSTGRES_PORT = your_db_port
  POSTGRES_HOST = your_host_postgres_db ( if you using app with docker, you should write host.docker.internal, else write url )
  
  REDIS_PORT = redis_db_port
  REDIS_HOST = your_host_redis_for_db ( same situation with docker for this field )
  
  BOT_TOKEN = your_bot_token
  
  API_URL = your_API_url ( check port in this url and dockerfile in backend root (default starting on 8000 port ) )
  
3. To start with docker from base project root:
   ```sh
   docker-compose up --build
   ```
4. Or to start from cmd you need start main files from backend and tg_bot directories.
   ```sh
   uvicorn main:app --reload --port 8000
   ```
   To start backend your need go to backend directory and start command. It start back with uvicorn on 8000 port.

   ```sh
   python main.py
   ```
   To start bot your need go to tg_bot directory and start command

## License

[MIT](https://choosealicense.com/licenses/mit/)
