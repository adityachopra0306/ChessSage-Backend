# ChessSage Backend

![status](https://img.shields.io/badge/status-WIP-yellow)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.1-teal?logo=fastapi)
![Redis](https://img.shields.io/badge/Redis-Upstash-critical?logo=redis)
![Pandas](https://img.shields.io/badge/Pandas-2.3.0-lightgrey?logo=pandas)
![license](https://img.shields.io/badge/license-MIT-green)

A FastAPI-based backend powering **ChessSage** – a smart chess coaching assistant that integrates Chess.com data and Gemini to generate personalized feedback, statistical breakdowns, and in-depth game reviews.

**Note**: The backend is **not** production-ready. Major features, including routing for some components, are still being implemented.

### The link to the **ChessSage** frontend can be found [here](https://github.com/adityachopra0306/ChessSage).

---

## Current Components

- `utils/`: Helper functions for:
  - API key selection and management
  - Prompt formatting
  - Date/time formatting
  - Safe accessors for nested JSON
- `services/`: Core logic for:
  - Fetching user data from Chess.com API
  - Analysis of played games and profile statistics
  - Prompt generation for Gemini
  - Game evaluation
- `routers/`: FastAPI route handlers for:
  - Setting and retrieving user configuration
  - Fetching Chess.com profile, stats, and games
  - Generating basic and per-mode detailed statistics 
- `scripts/`: Module-level Integration Testing scripts for verifying logic before full router integration

---

## Planned Modules

- `routers/`: Additional routers for:
  - Gemini API calls
  - Single game review endpoints
- `main.py`: FastAPI application setup and route mounting
- Deployment scripts, Docker Setup

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/adityachopra0306/ChessSage-Backend.git
cd ChessSage-Backend
```
### 2. Create and activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
REDIS_URL=<upstash_redis_url>
REDIS_TOKEN=<upstash_token>
GEMINI_API_KEYS=<comma_separated_api_keys>
```

### 5. Run the App
```bash
uvicorn main:app --reload
```
---

### API Endpoints

- #### Health Check
  ```bash
  GET /health
  ```
    Returns 200 if service is up

- #### User Configuration
  ```bash
  POST /config/{user_id}
  ```
    Stores user config: tone, background, response length, timeframe, etc.

- #### Data Fetching
  ```bash
  POST /profile_data/{user_id}
  ```
    Fetches and processes profile, stats, and games in one go

- #### Statistics
  ```bash
  POST /stats/basic/{user_id}
  ```
    Returns general stats summary

  ```bash
  POST /stats/detail/{user_id}/{mode_key}
  ```
    Detailed stats per game mode: `rapid`, `blitz`, `bullet`, `daily`
  
---

## Tech Stack

| Technology         | Purpose                                           |
|--------------------|---------------------------------------------------|
| `FastAPI`          | Web framework for building async APIs             |
| `httpx`            | Async HTTP requests (used for Chess.com API calls)|
| `upstash-redis`    | Caching layer via Upstash                         |
| `Pandas`, `NumPy`  | Data processing and statistical analysis          |
| `python-chess`     | Chess PGN parsing and board logic                 |
| `google-genai`     | Gemini LLM integration                            |

## Testing Scripts

The `scripts/` directory contains standalone scripts used to manually verify core modules before full router integration. These scripts test key functionality like data fetching, Gemini prompting, and preprocessing.

### Run individual tests with:

```bash
python scripts/test_chess_api.py
python scripts/test_get_stats.py
python scripts/test_gemini_api.py
python scripts/test_preprocess.py
```

---

## Project Structure

```
sage-backend
├── routers/
│   ├── set_user.py 
│   ├── get_profile_data.py
│   ├── get_stats.py
├── scripts/  
│   ├── test_chess_api.py  
│   ├── test_gemini_api.py  
│   ├── test_get_stats.py  
│   └── test_preprocess.py
├── services/  
│   ├── chess_api.py  
│   ├── game_review.py  
│   ├── prompting.py  
│   ├── get_stats.py  
│   └── preprocess.py  
├── utils/  
│   ├── api_utils.py  
│   ├── testing_utils.py  
│   └── utils.py  
├── main.py  
├── README.md  
|── requirements.txt
└── LICENSE
```

## License
This project is licensed under the MIT License. See the [License File](./LICENSE) for details.
