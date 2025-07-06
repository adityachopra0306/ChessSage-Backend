# ChessSage Backend

![status](https://img.shields.io/badge/status-WIP-yellow)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

This project powers the backend for **ChessSage**, an intelligent chess analytics and coaching assistant that leverages the Chess.com API and Gemini to deliver personalized feedback and statistical breakdowns of player profiles, along with detailed game review and analysis of specific games.

**Note**: The backend is **not** production-ready. Major features, including routing, are still being implemented.

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
- `scripts/`: Local test scripts for verifying logic before full router integration

---

## Planned Modules

- `routers/`: FastAPI routers for:
  - User info handling
  - Chess.com profile + stats analysis
  - Game review endpoints
- `main.py`: FastAPI application setup and route mounting
- Deployment scripts and Docker setup

---

## Project Structure

```
sage-backend  
├── scripts/  
│   ├── test_chess_api.py  
│   ├── test_gemini_api.py  
│   ├── test_get_stats.py  
│   └── test_preprocess.py  
├── services/  
│   ├── chess_api.py  
│   ├── game_review.py  
│   ├── gemini_api.py  
│   ├── get_stats.py  
│   └── preprocess.py  
├── utils/  
│   ├── api_utils.py  
│   ├── testing_utils.py  
│   └── utils.py  
├── main.py  
├── README.md  
└── requirements.txt  
```

## License
This project is licensed under the MIT License.