import { useState, useEffect } from "react";

import SpeechRecognition, {
    useSpeechRecognition,
} from "react-speech-recognition";

function InputBox({ onSend }) {

    const [question, setQuestion] = useState("");

    const {
        transcript,
        listening,
        resetTranscript,
        browserSupportsSpeechRecognition,
    } = useSpeechRecognition();

    // Update input whenever speech changes
    useEffect(() => {
        if (transcript) {
            setQuestion(transcript);
        }
    }, [transcript]);

    const handleSend = () => {

        const text = question.trim();

        if (!text) return;

        onSend(text);

        setQuestion("");

        resetTranscript();
    };

    const startListening = () => {
        resetTranscript();

        SpeechRecognition.startListening({
            continuous: true,
            language: "en-US",
        });
    };

    const stopListening = () => {
        SpeechRecognition.stopListening();
    };

    if (!browserSupportsSpeechRecognition) {
        return (
            <p>Your browser doesn't support Speech Recognition.</p>
        );
    }

    return (
        <div
            style={{
                display: "flex",
                gap: "10px",
                padding: "15px",
                alignItems: "center",
            }}
        >
            <input
                type="text"
                placeholder="Ask anything..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        handleSend();
                    }
                }}
                style={{
                    flex: 1,
                    padding: "12px",
                    borderRadius: "8px",
                    border: "1px solid #ccc",
                    fontSize: "16px",
                    color: "#000",
                    background: "#fff",
                }}
            />

            {!listening ? (
                <button
                    onClick={startListening}
                    style={{
                        padding: "12px 16px",
                        borderRadius: "8px",
                        cursor: "pointer",
                        background: "#1976d2",
                        color: "white",
                        border: "none",
                    }}
                >
                    🎤
                </button>
            ) : (
                <button
                    onClick={stopListening}
                    style={{
                        padding: "12px 16px",
                        borderRadius: "8px",
                        cursor: "pointer",
                        background: "red",
                        color: "white",
                        border: "none",
                    }}
                >
                    ⏹
                </button>
            )}

            <button
                onClick={handleSend}
                style={{
                    padding: "12px 20px",
                    borderRadius: "8px",
                    cursor: "pointer",
                    background: "#16a34a",
                    color: "white",
                    border: "none",
                    fontWeight: "bold",
                }}
            >
                Send
            </button>
        </div>
    );
}

export default InputBox;