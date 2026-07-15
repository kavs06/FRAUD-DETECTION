import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

// ------------------------------------
// Normal Chat API
// ------------------------------------
export const askQuestion = async (question) => {

    const response = await axios.post(
        `${API_URL}/chat`,
        {
            question,
        }
    );

    return response.data;
};

// ------------------------------------
// Streaming Chat API
// ------------------------------------
export const streamQuestion = async (
    question,
    onChunk
) => {

    const response = await fetch(
        `${API_URL}/chat-stream`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify({
                question,
            }),
        }
    );

    if (!response.ok) {

        throw new Error("Backend not connected.");
    }

    const reader = response.body.getReader();

    const decoder = new TextDecoder();

    while (true) {

        const { done, value } =
            await reader.read();

        if (done) break;

        const chunk = decoder.decode(
            value,
            {
                stream: true,
            }
        );

        onChunk(chunk);
    }
};