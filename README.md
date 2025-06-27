# 🤖 AI Investment Agent - Open Source Edition

A completely open-source AI-powered investment analysis tool that uses local Ollama models to analyze stock valuations and compare them against sector peers.

## ✨ Features

- **Local AI Processing**: Uses Ollama models running locally on your machine
- **Sector Analysis**: Automatically detects stock sectors and compares against peers
- **Valuation Metrics**: P/E, P/B, PEG ratios and more
- **Real-time Data**: Live stock data via Yahoo Finance
- **No API Keys Required**: Completely free and open source

## 🚀 Get Started

### 1. Install Ollama

First, install Ollama on your system:

**macOS:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/download)

### 2. Pull a Model

Pull one of the supported models:

```bash
# Option 1: Llama 3.2 (recommended)
ollama pull llama3.2

# Option 2: Mistral (faster, smaller)
ollama pull mistral

# Option 3: Code Llama (good for analysis)
ollama pull codellama
```

### 3. Install Python Dependencies

**Option A: Using pip (recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Using conda (alternative)**
```bash
# Create a new conda environment
conda create -n ai-stock-picker python=3.11

# Activate the environment
conda activate ai-stock-picker

# Install dependencies
pip install -r requirements.txt
```

**Note**: You can also use conda to install some packages, but pip is recommended for this project as some packages are only available via pip.

### 4. Start Ollama

In a terminal, start the Ollama service:

```bash
ollama serve
```

### 5. Run the Application

In another terminal:

```bash
streamlit run app.py
```

## 📊 How to Use

1. **Select Model**: Choose from available Ollama models (llama3.2, mistral, codellama, etc.)
2. **Enter Stock Symbol**: Type a stock symbol (e.g., AAPL, MSFT, TSLA)
3. **View Analysis**: The app will:
   - Detect the stock's sector
   - Fetch sector constituents
   - Calculate valuation metrics
   - Generate AI-powered analysis

## 🧠 Supported Models

- **llama3.2**: Best overall performance (recommended)
- **llama3.1**: Good balance of speed and quality
- **mistral**: Fast and efficient
- **codellama**: Good for analytical tasks
- **qwen2.5**: Alternative option

## 🔧 Troubleshooting

### Ollama Connection Issues

If you see "Cannot connect to Ollama":
1. Ensure Ollama is installed: `ollama --version`
2. Start the service: `ollama serve`
3. Check if it's running: `curl http://localhost:11434/api/tags`

### Model Not Found

If you get a model error:
1. Pull the model: `ollama pull llama3.2`
2. List available models: `ollama list`

### Performance Tips

- Use `mistral` for faster responses
- Use `llama3.2` for better analysis quality
- Ensure you have sufficient RAM (8GB+ recommended)

## 🏗️ Architecture

- **Frontend**: Streamlit web interface
- **AI Engine**: Ollama with local models
- **Data Source**: Yahoo Finance via yfinance
- **Analysis**: Sector-based peer comparison

## 📈 Example Output

The app provides:
- Stock sector identification
- Valuation metrics comparison
- AI-generated investment analysis
- Peer comparison tables


