import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function Message({ sender, text }) {
    const isUser = sender === "user";

    return (
        <div
            style={{
                display: "flex",
                justifyContent: isUser ? "flex-end" : "flex-start",
                margin: "18px 0",
            }}
        >
            <div
                style={{
                    maxWidth: "78%",
                    padding: "16px 20px",
                    borderRadius: "18px",
                    background: isUser ? "#1976d2" : "#ffffff",
                    color: isUser ? "#ffffff" : "#222222",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                    border: isUser ? "none" : "1px solid #dcdcdc",
                    lineHeight: "1.7",
                    wordBreak: "break-word",
                }}
            >
                <div
                    style={{
                        fontWeight: "bold",
                        marginBottom: "10px",
                        color: isUser ? "#ffffff" : "#1565c0",
                        fontSize: "18px",
                    }}
                >
                    {isUser ? "👤 You" : "🤖 Healthcare AI"}
                </div>

                <div
                    style={{
                        color: isUser ? "#ffffff" : "#222222",
                        fontSize: "16px",
                    }}
                >
                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                            p: ({ children }) => (
                                <p style={{ color: isUser ? "#fff" : "#222", margin: "8px 0" }}>
                                    {children}
                                </p>
                            ),
                            li: ({ children }) => (
                                <li style={{ color: isUser ? "#fff" : "#222" }}>
                                    {children}
                                </li>
                            ),
                            strong: ({ children }) => (
                                <strong style={{ color: isUser ? "#fff" : "#000" }}>
                                    {children}
                                </strong>
                            ),
                            h1: ({ children }) => (
                                <h1 style={{ color: isUser ? "#fff" : "#000" }}>
                                    {children}
                                </h1>
                            ),
                            h2: ({ children }) => (
                                <h2 style={{ color: isUser ? "#fff" : "#000" }}>
                                    {children}
                                </h2>
                            ),
                            h3: ({ children }) => (
                                <h3 style={{ color: isUser ? "#fff" : "#000" }}>
                                    {children}
                                </h3>
                            ),
                            code: ({ children }) => (
                                <code
                                    style={{
                                        background: "#f4f4f4",
                                        color: "#d63384",
                                        padding: "2px 6px",
                                        borderRadius: "4px",
                                    }}
                                >
                                    {children}
                                </code>
                            ),
                        }}
                    >
                        {text}
                    </ReactMarkdown>
                </div>
            </div>
        </div>
    );
}

export default Message;