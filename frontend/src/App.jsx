import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function App() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const onSubmit = async (event) => {
    event.preventDefault();

    if (!topic.trim()) {
      setError("Please enter a topic before running research.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE}/research`, {
        topic: topic.trim(),
      });

      if (response.data?.error) {
        setError(response.data.error);
      } else {
        setResult(response.data);
      }
    } catch (requestError) {
      const message =
        requestError?.response?.data?.detail ||
        requestError?.message ||
        "Failed to contact backend. Ensure API is running on port 8000.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <h1>Multi-Agent Research Assistant</h1>
        <p>Enter a topic and generate a research report with critique.</p>
      </header>

      <form className="research-form" onSubmit={onSubmit}>
        <label htmlFor="topic">Research Topic</label>
        <textarea
          id="topic"
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
          rows={3}
          placeholder="Example: Impact of AI on healthcare diagnostics in 2026"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Running research..." : "Run Research"}
        </button>
      </form>

      {error && <section className="card error">{error}</section>}

      {result && (
        <section className="results">
          <article className="card">
            <h2>Report</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.report || "No report returned."}
            </ReactMarkdown>
          </article>

          <article className="card">
            <h2>Critique</h2>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {result.critique || "No critique returned."}
            </ReactMarkdown>
          </article>

          <article className="card">
            <h2>Search Results</h2>
            <pre>{result.search_results || "No search results returned."}</pre>
          </article>

          <article className="card">
            <h2>Scraped Content</h2>
            <pre>{result.scraped_content || "No scraped content returned."}</pre>
          </article>
        </section>
      )}
    </main>
  );
}
