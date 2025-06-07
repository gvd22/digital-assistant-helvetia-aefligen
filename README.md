# digital-assistant-helvetia-aefligen

This project provides a crawler and a simple Gradio interface for querying indexed content.

Copy `src/.env.example` to `src/.env` and fill in your API credentials before running the application. The app uses Mistral AI, so provide `MISTRAL_API_KEY` alongside your `PINECONE_API_KEY`.

## Environment variables

The application reads the following variables from `src/.env`:

```bash
PINECONE_API_KEY=your-pinecone-api-key
MISTRAL_API_KEY=your-mistral-api-key
PINECONE_INDEX=helvetia-aefligen-dev
```

These credentials are required by both the crawler and the Gradio UI.

## Running the crawler and indexer

Build the images and then run the crawler to create the Pinecone index:

```bash
docker compose build
docker compose run --rm indexer
```

This command fetches the website content, converts it to Markdown and uploads the chunks to the configured Pinecone index.

## Starting the Gradio UI

Start the chatbot interface with Docker Compose:

```bash
docker compose up chatbot
```

The UI will be available at [http://localhost:5000](http://localhost:5000).

## Running with Docker Compose

Build and start the chatbot and indexer with one command:

```bash
docker compose up --build
```
