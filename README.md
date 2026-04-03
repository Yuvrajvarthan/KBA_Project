# Knowledge Base AI Platform (KBA)

A RAG-based conversational AI platform for document analysis and knowledge retrieval.

## Project Overview

This platform allows users to:
- Upload and process documents (PDF, DOCX, TXT)
- Ingest content from YouTube videos and websites
- Ask questions and get contextual answers using AI
- Retrieve relevant information from the knowledge base

## Tech Stack

### Backend
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **ChromaDB** - Vector database for embeddings
- **Google Gemini** - Embeddings and chat generation
- **Pydantic** - Data validation
- **pdfplumber** - PDF parsing
- **python-docx** - DOCX parsing
- **BeautifulSoup4** - HTML parsing
- **youtube-transcript-api** - YouTube transcripts

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

## Project Structure

```
KBA_Project/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration and settings
│   │   ├── models/         # Data models
│   │   ├── routers/        # API routes
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI app entry point
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── .env               # Environment variables (create this)
├── frontend/
│   ├── app/               # Next.js app directory
│   ├── components/        # React components
│   ├── lib/              # API utilities
│   ├── types/            # TypeScript types
│   └── package.json      # Node.js dependencies
├── .env.example          # Environment variables template (copy to backend/.env)
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- Google Gemini API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `backend/.env.example`:
```bash
cp .env.example .env
```

5. Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_actual_api_key_here
```

6. Run the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Health
- `GET /api/health` - Health check

### Ingestion
- `POST /api/ingest/document` - Upload document files
- `POST /api/ingest/youtube` - Ingest YouTube transcript
- `POST /api/ingest/web` - Ingest website content
- `GET /api/ingest/stats` - Get ingestion statistics

### Chat
- `POST /api/chat/message` - Send chat message
- `POST /api/chat/add-context` - Add conversation context
- `POST /api/chat/clear-context` - Clear conversation context
- `POST /api/chat/clear-history` - Clear chat history

## Development Status

### Stage 1: ✅ Completed
- Project structure created
- Backend scaffold with FastAPI
- Frontend scaffold with Next.js
- Basic configuration files
- Environment variables setup
- Proper error handling and validation
- Git ignore file added
- Correct run commands documented

### Next Stages
- Stage 2: Ingestion pipeline implementation
- Stage 3: Embeddings and vector database
- Stage 4: Chat and RAG API
- Stage 5: Frontend UI and integration
- Stage 6: Testing and final delivery

## Notes

- ChromaDB data will be stored in `./chroma_db` directory
- Maximum file size for uploads: 10MB
- Supported file types: PDF, DOCX, TXT
- The system uses cosine similarity for document retrieval
- Text chunks are 500 characters with 100 character overlap
- Backend `.env` file should be created in the `backend/` directory
- Get your Gemini API key from: https://makersuite.google.com/app/apikey
- Frontend dependencies must be installed with `npm install` before running
- Backend will fail to start if GEMINI_API_KEY is not properly configured 
