import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Hello! I am the FraudGuard AI Assistant. I can help you investigate flagged providers, explain risk scores, and query Medicare fraud policies. How can I assist you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  const { token } = useAuth(); // Use the JWT token for auth if needed

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInput('');
    setLoading(true);

    try {
      const res = await axios.post('http://127.0.0.1:8000/chat', {
        provider_id: "P123",
        message: userMessage
      }, {
        // Pass token in headers if you want to secure the backend /chat route later
        // headers: { Authorization: `Bearer ${token}` }
      });
      
      setMessages(prev => [...prev, { role: 'system', content: res.data.response }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'system', content: 'Sorry, I encountered an error connecting to the intelligence engine.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-10rem)] flex flex-col bg-white/60 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white overflow-hidden animate-fade-in-up">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900 to-indigo-800 p-6 flex items-center relative overflow-hidden">
        <div className="absolute right-0 top-0 w-64 h-64 bg-indigo-500 rounded-full mix-blend-screen filter blur-[80px] opacity-40"></div>
        <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center mr-4 shadow-[inset_0_0_15px_rgba(255,255,255,0.2)] border border-white/20">
          <Bot className="w-7 h-7 text-indigo-300" />
        </div>
        <div className="relative z-10">
          <h2 className="text-xl font-black text-white tracking-wider flex items-center">
            RAG Intelligence Engine
            <Sparkles className="w-4 h-4 ml-2 text-indigo-300 animate-pulse" />
          </h2>
          <p className="text-sm text-indigo-200 font-medium mt-1">Powered by Gemini AI & Local FAISS Vectors</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 bg-transparent">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`} style={{ animationDelay: `${idx * 0.1}s` }}>
            <div className={`flex max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              
              <div className={`flex-shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg ${msg.role === 'user' ? 'bg-gradient-to-br from-indigo-500 to-purple-600 ml-4' : 'bg-gradient-to-br from-slate-700 to-slate-900 mr-4'}`}>
                {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-indigo-400" />}
              </div>
              
              <div className={`p-5 rounded-3xl shadow-sm text-[15px] leading-relaxed ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-sm' : 'bg-white/80 backdrop-blur-md border border-white text-slate-800 rounded-tl-sm shadow-[0_4px_20px_rgb(0,0,0,0.03)]'}`}>
                <p className="whitespace-pre-wrap font-medium">{msg.content}</p>
              </div>

            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start animate-fade-in-up">
            <div className="flex max-w-[80%] flex-row">
              <div className="flex-shrink-0 w-10 h-10 rounded-2xl bg-gradient-to-br from-slate-700 to-slate-900 flex items-center justify-center mr-4 shadow-lg">
                <Bot className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="p-5 rounded-3xl bg-white/80 backdrop-blur-md border border-white shadow-[0_4px_20px_rgb(0,0,0,0.03)] rounded-tl-sm flex items-center space-x-3">
                <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce"></div>
                <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white/80 backdrop-blur-md border-t border-white shadow-[0_-10px_40px_rgb(0,0,0,0.03)] relative z-10">
        <form onSubmit={handleSend} className="flex gap-3 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about a provider, claim patterns, or policies..."
            className="flex-1 py-4 px-6 bg-slate-100/50 border border-slate-200 hover:border-indigo-300 rounded-2xl focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all font-medium text-slate-700 placeholder-slate-400"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white rounded-2xl transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:-translate-y-0.5"
          >
            <Send className="w-5 h-5 mr-2" />
            <span className="font-bold tracking-wide">Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chatbot;
