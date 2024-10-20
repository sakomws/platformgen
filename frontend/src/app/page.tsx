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
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-gray-50 text-gray-800">
      <main className="flex flex-col lg:flex-row gap-10 w-full max-w-7xl">
        {/* Inputs and Updated Requirements on the Left (Smaller Area) */}
        <div className="flex flex-col gap-6 w-full lg:w-1/3">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">PlatformGen</h1>
          <p className="text-gray-600 text-center mb-6">Autonomous Dependency Management</p>
          <form onSubmit={handleSubmit} className="flex flex-col gap-5 w-full">
            <div className="w-full">
              <label className="block mb-2 text-gray-700 font-medium">GitHub Owner:</label>
              <input
                type="text"
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                required
                className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
              />
            </div>
            <div className="w-full">
              <label className="block mb-2 text-gray-700 font-medium">Repository Name:</label>
              <input
                type="text"
                value={repoName}
                onChange={(e) => setRepoName(e.target.value)}
                required
                className="w-full border border-gray-300 px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition duration-300 ease-in-out font-semibold disabled:bg-blue-400"
            >
              {loading ? 'Running...' : 'Run All'}
            </button>
          </form>

          {result && (
            <>
              <h2 className="text-lg font-semibold text-gray-900 mt-10">Updated Requirements:</h2>
              <pre className="bg-gray-100 p-4 rounded-lg mt-3 text-gray-800 whitespace-pre-wrap border border-gray-200">
                {result.updated_requirements}
              </pre>
            </>
          )}

          {error && (
            <div className="mt-8 w-full max-w-md text-red-600 bg-red-100 p-4 rounded-lg border border-red-200">
              <h2 className="text-lg font-semibold">Error:</h2>
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Separator Line */}
        <div className="hidden lg:block w-px bg-gray-300 mx-4"></div>

        {/* Summary of Changes on the Right (Larger Area) */}
        {result && (
          <div className="flex flex-col gap-6 w-full lg:w-2/3 bg-gray-100 p-6 rounded-lg border border-gray-200 shadow-md">
            <h2 className="text-lg font-semibold text-gray-900">Summary of Changes:</h2>

            {/* Llama 3.2 Summary */}
            <div className="bg-gray-50 p-4 rounded-lg text-gray-800 border border-gray-200 overflow-y-auto max-h-80">
              <h3 className="font-bold text-xl text-blue-600 mb-3">Llama 3.2 Summary:</h3>
              <pre className="bg-gray-50 p-3 rounded-lg border-l-4 border-blue-600 pl-3 shadow-sm overflow-x-auto whitespace-pre-wrap break-words">
                {result.diff_summary?.split("### Llama 3.2 Summary:")[1].trim()}
              </pre>
            </div>

            {/* OpenAI Summary */}
            <div className="bg-gray-50 p-4 rounded-lg text-gray-800 border border-gray-200 overflow-y-auto max-h-80">
              <h3 className="font-bold text-xl text-green-600 mt-6 mb-3">OpenAI Summary:</h3>
              <pre className="bg-gray-50 p-3 rounded-lg border-l-4 border-green-600 pl-3 shadow-sm overflow-x-auto whitespace-pre-wrap break-words">
                {result.diff_summary?.split("### Llama 3.2 Summary:")[0].replace("### OpenAI Summary:", "").trim()}
              </pre>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
