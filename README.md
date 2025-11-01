# LLM URL Finder: Resilient Query Generation Tool

The **LLM URL Finder** is a sophisticated Python tool that leverages a local Large Language Model (LLM) to generate, sanitize, and validate search queries for security and due diligence tasks.

This project demonstrates core **Product Security Engineering principles** such as **resilience**, **input validation**, and **data integrity** in an LLM-powered pipeline.

## 🛡️ Product Security Engineering Highlights

| Feature | Security Principle Demonstrated |
| :--- | :--- |
| **JSON Repair** (`json-repair`) | **Resilience / Error Handling:** The pipeline automatically detects and fixes malformed JSON output from the LLM, preventing crashes and ensuring the pipeline remains stable under non-ideal conditions. |
| **URL Encoding** (`urllib.parse`) | **Input Validation / Sanitization:** All extracted queries are safely URL-encoded (`quote_plus`) before generating search links, mitigating the risk of injection vulnerabilities in downstream web interactions. |
| **Cross-Validation** | **Data Integrity / Trust but Verify:** Generated queries are validated against the simulated results of three independent search engines (Google, Bing, DuckDuckGo) to reduce reliance on a single source (the LLM). |
| **Confidence Scoring** | **Risk Prioritization:** Results are assigned a quantitative confidence score (**HIGH 🟢, MEDIUM 🟡, or LOW 🔴**) to help an analyst prioritize manual review tasks. |

***

## 🚀 Installation & Setup

### Prerequisites

1.  **Ollama:** Ensure the Ollama server is running locally with the `llama3` model downloaded.
    ```bash
    ollama run llama3
    ```
2.  **Python:** Python 3.8+ is required.

### Project Structure

Clone the repository and navigate into the directory:

```bash
git clone [https://github.com/ronaldon2023/llm_urlfinder](https://github.com/ronaldon2023/llm_urlfinder)
cd llm_urlfinder
