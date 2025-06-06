# digital-assistant-helvetia-aefligen

This project provides a crawler and a simple Gradio interface for querying indexed content.

Copy `src/.env.example` to `src/.env` and fill in your API credentials before running the application.

## Environment variables

The application reads the following variables from `src/.env`:

```bash
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
```

These credentials are required by both the crawler and the Gradio UI.

## Running the crawler and indexer

You can run the crawler and build the Pinecone index using Docker Compose:

```bash
docker compose run --rm indexer
```

This command fetches the website content, converts it to Markdown and uploads the chunks to the configured Pinecone index.

## Starting the Gradio UI

Launch the chatbot interface with Docker Compose:

```bash
docker compose up chatbot
```

The UI will be available at [http://localhost:5000](http://localhost:5000).
