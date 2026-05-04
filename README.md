# Web Data Extraction System: Sequential vs Parallel

A high-performance asynchronous web scraping dashboard designed to benchmark execution models. This system compares synchronous (Sequential) and asynchronous (Parallel) processing to demonstrate performance speedups in I/O-bound web operations.

## 🚀 Key Features

- **Clean Architecture**: Decoupled design split into `Core` (logic), `Engines` (execution), and `UI` (presentation).
- **Dual Engine Models**:
  - **Sequential Engine**: Standard synchronous requests with linear execution.
  - **Parallel Engine**: High-speed asynchronous engine built on `aiohttp` and `asyncio` with exponential backoff retries.
- **Intelligent Extraction**:
  - Automated page title resolution.
  - Text normalization and word count analysis.
  - **Advanced NLP**: High-precision keyword extraction using a custom 100+ word stopword dictionary.
  - Unique link discovery and deduplication.
- **Real-Time Benchmarking**:
  - Visual speedup multiplier (e.g., "7.5x faster").
  - Throughput metrics (Requests per Second).
  - Live progress counters for both engines.
- **Modern UI**: A sleek, dark-themed dashboard focused on developer productivity and data visualization.

## 📁 Project Structure

```text
├── main.py                 # Application Entry Point
├── core/
│   ├── domain.py           # Business Models & Data Structures
│   └── parser.py           # Scraping Logic & NLP processing
├── engines/
│   ├── sequential_engine.py# Synchronous I/O Logic
│   └── parallel_engine.py  # Asynchronous I/O Logic
└── ui/
    └── gui.py              # Tkinter Dashboard Framework
```

## 🛠️ Installation

### 1. Requirements
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
```bash
pip install beautifulsoup4 aiohttp requests lxml
```
*Note: If pip is not in your PATH on Windows, use:*
```powershell
python -m pip install beautifulsoup4 aiohttp requests lxml
```

## 🎮 How to Use

1. **Launch the Dashboard**:
   ```bash
   python main.py
   ```
2. **Prepare URL List**: Create a `.txt` file containing the full URLs you want to scrape (one per line, starting with `http`).
3. **Upload & Run**: Click **"Upload Your URLs (.txt)"** in the dashboard, then hit **"Start Extraction"**.

## 📊 Evaluation & Metrics

The system evaluates the following metrics for comparison:
- **Execution Time**: The total wall-clock time from start to completion.
- **Success Rate**: Number of URLs successfully processed vs. network failures.
- **Throughput (Req/s)**: Average requests handled per second.
- **Speedup Multiplier**: The calculated performance ratio ($T_{seq} / T_{par}$).

## 🛡️ Stability Features

- **Rate Limiting**: Parallel engine utilizes an asynchronous semaphore limit to prevent IP blocking.
- **Exponential Backoff**: Integrated retry logic that progressively waits longer between failed requests to handle network congestion.
- **Thread Safety**: Backend analysis runs on separate threads to ensure the UI remains responsive during heavy scraping tasks.
