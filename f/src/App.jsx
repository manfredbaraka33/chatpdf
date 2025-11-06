import React, { useState, useEffect } from "react";
import FileUpload from "./components/FileUpload";
import QuestionBox from "./components/QuestionBox";
import axios from "axios";

function App() {
  const [isReady, setIsReady] = useState(true); // backend ready
  const [polling, setPolling] = useState(false);

  // Poll /status/ endpoint
  const checkStatus = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/status/");
      setIsReady(res.data.ready);
      if (!res.data.ready) {
        setTimeout(checkStatus, 1000); // poll every second
      } else {
        setPolling(false);
      }
    } catch (err) {
      console.error(err);
      setTimeout(checkStatus, 2000);
    }
  };

  const handleUploadComplete = () => {
    setIsReady(false);
    if (!polling) {
      setPolling(true);
      checkStatus();
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">📄 ChatPDF Q&A</h1>

      <div className="w-full max-w-3xl bg-white p-6 rounded-xl shadow-md">
        <FileUpload onUploadComplete={handleUploadComplete} />
      </div>

      <div className="w-full max-w-3xl bg-white p-6 rounded-xl shadow-md mt-6">
        <QuestionBox isReady={isReady} />
      </div>
    </div>
  );
}

export default App;
