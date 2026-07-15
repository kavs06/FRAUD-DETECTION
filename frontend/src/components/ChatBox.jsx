import { useState, useRef, useEffect } from "react";

import Message from "./Message";
import InputBox from "./InputBox";
import Loading from "./Loading";

import { streamQuestion } from "../services/api";

function ChatBox() {

    const [messages, setMessages] = useState([
        {
            sender: "assistant",
            text:
                "👋 Hello! I'm your **Healthcare Fraud RAG Chatbot**.\n\n" +
                "I can help you with:\n\n" +
                "• Provider Investigation Reports\n" +
                "• Healthcare Fraud Detection\n" +
                "• Medical Information\n" +
                "• General Health Questions\n\n" +
                "Ask me anything!",
        },
    ]);

    const [loading, setLoading] = useState(false);

    const chatEndRef = useRef(null);

    useEffect(() => {

        chatEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });

    }, [messages]);

    //---------------------------------------------------

    const sendQuestion = async (question) => {

        if (!question.trim()) return;

        setLoading(true);

        // Add user message
        setMessages((prev) => [
            ...prev,
            {
                sender: "user",
                text: question,
            },
            {
                sender: "assistant",
                text: "",
            },
        ]);

        try {

            await streamQuestion(

                question,

                (chunk) => {

                    setMessages((prev) => {

                        const updated = [...prev];

                        updated[updated.length - 1] = {
                            ...updated[updated.length - 1],
                            text:
                                updated[updated.length - 1].text +
                                chunk,
                        };

                        return updated;

                    });

                }

            );

        }

        catch (err) {

            setMessages((prev) => {

                const updated = [...prev];

                updated[updated.length - 1] = {

                    sender: "assistant",

                    text:
                        "❌ Unable to connect to backend.",

                };

                return updated;

            });

        }

        setLoading(false);

    };

    //---------------------------------------------------

    const suggestions = [

        "Tell me about PRV56689",

        "Which provider has high fraud risk?",

        "Explain phantom billing",

        "What is diabetes?",

        "What is blood pressure?",

    ];

    //---------------------------------------------------

    return (

        <div>

            <div

                style={{

                    height: "70vh",

                    overflowY: "auto",

                    border: "1px solid #ddd",

                    borderRadius: "12px",

                    padding: "20px",

                    background: "#fafafa",

                }}

            >

                {messages.map((msg, index) => (

                    <Message

                        key={index}

                        sender={msg.sender}

                        text={msg.text}

                    />

                ))}

                {loading && <Loading />}

                <div ref={chatEndRef}></div>

            </div>

            <div

                style={{

                    marginTop: "15px",

                    marginBottom: "15px",

                }}

            >

                <strong>💡 Suggested Questions</strong>

                <div

                    style={{

                        display: "flex",

                        flexWrap: "wrap",

                        gap: "10px",

                        marginTop: "10px",

                    }}

                >

                    {suggestions.map((question) => (

                        <button

                            key={question}

                            onClick={() => sendQuestion(question)}

                            style={{

                                padding: "8px 14px",

                                borderRadius: "20px",

                                border: "1px solid #1976d2",

                                background: "#1976d2",

                                color: "white",

                                cursor: "pointer",

                            }}

                        >

                            {question}

                        </button>

                    ))}

                </div>

            </div>

            <InputBox onSend={sendQuestion} />

        </div>

    );

}

export default ChatBox;