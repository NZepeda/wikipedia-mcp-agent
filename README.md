# MCP Tutorial - Wikipedia AI Assistant

Interactive AI assistant powered by MCP (Model Context Protocol) that searches Wikipedia using GPT-4.

## Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Configure OpenAI API key:**

   Create a `.env` file in the project root:

   ```bash
   OPENAI_API_KEY=your-key-here
   ```

3. **Run:**

   ```bash
   uv run python main.py
   ```

4. **Interact:**

   ```
   You: Tell me about the Eiffel Tower
   AI: [Fetches and summarizes from Wikipedia]

   You: exit
   ```

## Requirements

- Python 3.12.6+
- OpenAI API key from [platform.openai.com](https://platform.openai.com/api-keys)
