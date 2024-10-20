"use client";

import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [owner, setOwner] = useState('');
  const [repoName, setRepoName] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/run_all', {
        owner: owner,
        repo_name: repoName
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-white text-black">
      <main className="flex flex-col gap-6 items-center">
        <h1 className="text-2xl font-bold">Platformgen - GitHub Repo Manager</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 items-center">
          <div>
            <label className="block mb-1">GitHub Owner:</label>
            <input
              type="text"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              required
              className="border px-4 py-2 rounded text-black"
            />
          </div>
          <div>
            <label className="block mb-1">Repository Name:</label>
            <input
              type="text"
              value={repoName}
              onChange={(e) => setRepoName(e.target.value)}
              required
              className="border px-4 py-2 rounded text-black"
            />
          </div>
          <button type="submit" disabled={loading} className="bg-blue-500 text-white px-6 py-2 rounded">
            {loading ? 'Running...' : 'Run All'}
          </button>
        </form>

        {result && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold">Updated Requirements:</h2>
            <pre className="bg-gray-100 p-4 rounded mt-2 text-black whitespace-pre-wrap">
              {result.updated_requirements}
            </pre>
          </div>
        )}

        {error && (
          <div className="mt-8 text-red-600">
            <h2 className="text-lg font-semibold">Error:</h2>
            <p>{error}</p>
          </div>
        )}
      </main>
    </div>
  );
}
