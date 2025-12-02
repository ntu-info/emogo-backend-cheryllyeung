[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/e7FBMwSa)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21914232&assignment_repo_type=AssignmentRepo)

# EmoGo Backend

EmoGo Backend API built with FastAPI and MongoDB Atlas.

## Data Export Page

**https://emogo-backend-cheryllyeung.onrender.com/export**

This page allows TAs to view and download all three types of data collected by the EmoGo frontend:
- Vlogs
- Sentiments
- GPS Coordinates

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome page |
| GET | `/export` | Data export/download page |
| GET | `/docs` | API documentation (Swagger UI) |
| POST | `/vlogs` | Create a new vlog entry |
| GET | `/vlogs` | Get all vlogs |
| POST | `/sentiments` | Create a new sentiment entry |
| GET | `/sentiments` | Get all sentiments |
| POST | `/gps` | Create a new GPS entry |
| GET | `/gps` | Get all GPS coordinates |

## Live Demo

- Backend URL: https://emogo-backend-cheryllyeung.onrender.com
- API Docs: https://emogo-backend-cheryllyeung.onrender.com/docs
