

// import React, { useState } from "react";
// import { askQuestion } from "../api";

// const QuestionBox = ({ isReady }) => {
//   const [query, setQuery] = useState("");
//   const [answer, setAnswer] = useState("");
//   const [loading, setLoading] = useState(false);

//   const handleAsk = async () => {
//     if (!query.trim()) return;
//     setLoading(true);
//     try {
//       const res = await askQuestion(query);
//       setAnswer(res.data.answer);
//     } catch (err) {
//       console.error(err);
//       setAnswer("Error getting answer.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="flex flex-col gap-4">
//       <input
//         type="text"
//         placeholder={
//           isReady
//             ? "Ask a question about your PDFs..."
//             : "PDFs are still processing, please wait..."
//         }
//         value={query}
//         onChange={(e) => setQuery(e.target.value)}
//         className="border border-gray-300 rounded p-2 w-full"
//         disabled={!isReady || loading}
//       />
//       <button
//         onClick={handleAsk}
//         disabled={!isReady || loading || !query.trim()}
//         className={`px-4 py-2 rounded text-white font-semibold  ${
//           !isReady || loading || !query.trim()
//             ? "bg-gray-400 cursor-not-allowed"
//             : "bg-green-600 hover:bg-green-700 cursor-pointer"
//         }`}
//       >
//         {loading ? "Thinking..." : "Ask"}
//       </button>

//       {!isReady && (
//         <p className="text-gray-500 italic">Waiting for embeddings to be ready...</p>
//       )}

//       {answer && (
//         <div className="mt-4 p-4 bg-gray-100 rounded shadow">
//           <h2 className="font-bold mb-2">Answer:</h2>
//           <p>{answer}</p>
//         </div>
//       )}
//     </div>
//   );
// };

// export default QuestionBox;


import { useState } from "react";
import { askQuestion } from "../api";

const QuestionBox = ({ isReady }) => {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await askQuestion(query);
      setAnswer(res.data.answer);
      setSources(res.data.sources || []);
    } catch (err) {
      console.error(err);
      setAnswer("Error getting answer.");
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">

      <input
        type="text"
        placeholder={
          isReady
            ? "Ask a question about your PDFs..."
            : "PDFs are still processing, please wait..."
        }
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="border border-gray-300 rounded p-2 w-full"
        disabled={!isReady || loading}
      />
      <button
        onClick={handleAsk}
        disabled={!isReady || loading || !query.trim()}
        className={`px-4 py-2 rounded text-white font-semibold ${
          !isReady || loading || !query.trim()
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-green-600 hover:bg-green-700"
        }`}
      >
        {loading ? "Thinking..." : "Ask"}
      </button>

      {answer && (
        <div className="mt-4 p-4 bg-gray-100 rounded shadow">
          <h2 className="font-bold mb-2">Answer:</h2>
          <p>{answer}</p>

          {sources.length > 0 && (
            <div className="mt-3 text-sm text-gray-600">
              <strong>Sources:</strong>
              <ul className="list-disc list-inside">
                {sources.map((src, idx) => (
                  <li key={idx}>{src}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QuestionBox;
