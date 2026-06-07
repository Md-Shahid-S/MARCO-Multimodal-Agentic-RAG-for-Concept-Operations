"use client";

import { useState, useRef, useEffect } from "react";
import { 
  Send, 
  Paperclip, 
  Menu, 
  Plus, 
  MessageSquare, 
  Settings, 
  User,
  Cpu,
  Search,
  LayoutDashboard,
  ChevronRight,
  Sparkles,
  MoreHorizontal,
  Box,
  Terminal,
  Activity,
  X,
  FileText,
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  Info
} from "lucide-react";

export default function Chat() {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState<any[]>([
    {
      role: "ai",
      type: "text",
      content: "Welcome to **MARCO**. I am your specialized architecture alignment assistant. I can help you evaluate architectural drift, validate CI/CD pipelines, and map concepts to the DevOps-MSA ontology. How can I assist you today?",
      time: ""
    }
  ]);

  useEffect(() => {
    setMessages(prev => [
      {
        ...prev[0],
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  }, []);

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl(null);
      return;
    }

    if (selectedFile.type.startsWith("image/")) {
      const objectUrl = URL.createObjectURL(selectedFile);
      setPreviewUrl(objectUrl);

      return () => URL.revokeObjectURL(objectUrl);
    } else {
      setPreviewUrl(null);
    }
  }, [selectedFile]);

  const handleSend = async (e?: React.FormEvent, presetMsg?: string) => {
    if (e) e.preventDefault();
    const textToSend = presetMsg || input;
    if (!textToSend.trim() && !selectedFile) return;

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const userMsg = { 
      role: "user", 
      type: "text",
      content: textToSend || (selectedFile ? `Analyzing artifact: ${selectedFile.name}` : ""), 
      time: now,
      fileName: selectedFile?.name
    };
    
    let fullQueryContext = textToSend;
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === "ai" && lastMessage.structuredData?.final_resolution?.includes("Clarification Needed")) {
        const originalQuery = messages[messages.length - 2]?.content || "";
        fullQueryContext = `[Original Query]: ${originalQuery}\n[AI Asked]: ${lastMessage.structuredData.final_resolution}\n[User Clarification]: ${textToSend}`;
      }
    }
    
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    const fileToUpload = selectedFile;
    setSelectedFile(null);
    setIsTyping(true);

    try {
      const formData = new FormData();
      if (fileToUpload) {
        formData.append("file", fileToUpload); // <-- The key is "file"
      }
      formData.append("query", fullQueryContext || "Analyze this artifact"); // <-- The key is "query"

      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = `Request failed with status: ${response.status}`;
        try {
          // Try to parse a JSON error response from the server
          const errorData = await response.json();
          errorMsg = errorData.detail || JSON.stringify(errorData);
        } catch (jsonError) {
          // If the response is not JSON, use the text body as the error.
          errorMsg = await response.text();
        }
        throw new Error(errorMsg);
      }

      const data = await response.json();
      
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          type: "structured",
          structuredData: data,
          reasoning: data.reasoning,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } catch (error) {
      console.error("File upload or chat request failed:", error);
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          type: "structured",
          structuredData: {
            status: "error",
            message: error instanceof Error ? `Error: ${error.message}` : "An unknown error occurred. Please check the console."
          },
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <div className="flex h-screen bg-[#F8F9FA] text-slate-900 font-sans selection:bg-slate-200 overflow-hidden">
      
      {/* Sidebar - Minimal Professional */}
      <aside 
        className={`${isSidebarOpen ? "w-[260px]" : "w-0"} transition-all duration-300 ease-in-out bg-white border-r border-slate-200 flex flex-col flex-shrink-0 overflow-hidden z-20`}
      >
        <div className="p-6 flex items-center gap-2.5">
          <div className="w-7 h-7 bg-slate-900 rounded flex items-center justify-center">
            <Box size={14} className="text-white" />
          </div>
          <span className="font-bold text-base tracking-tight text-slate-900 uppercase">MARCO</span>
        </div>
        
        <div className="px-4 mb-6">
          <button 
            onClick={() => setMessages(messages.slice(0, 1))}
            className="w-full flex items-center gap-2.5 bg-slate-900 text-white hover:bg-slate-800 rounded-lg px-4 py-2 text-xs font-bold transition-all"
          >
            <Plus size={14} />
            New Session
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-2 space-y-6">
          <nav>
            <h3 className="px-3 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Workspace</h3>
            <div className="space-y-0.5">
              <SidebarItem icon={<LayoutDashboard size={14} />} label="System Overview" active />
            </div>
          </nav>
        </div>

        <div className="p-4 mt-auto border-t border-slate-100">
          <div className="flex items-center gap-3 p-2 group cursor-pointer transition-all">
            <div className="w-8 h-8 rounded bg-slate-100 flex items-center justify-center border border-slate-200 overflow-hidden">
               <img src={`https://ui-avatars.com/api/?name=Suresh+Shahid&background=f8fafc&color=0f172a&bold=true`} alt="User" />
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="text-xs font-bold text-slate-800 truncate">Suresh Shahid</p>
              <p className="text-[10px] text-slate-400 truncate font-medium underline decoration-slate-200">Researcher</p>
            </div>
            <Settings size={14} className="text-slate-300 group-hover:text-slate-600 transition-colors" />
          </div>
        </div>
      </aside>

      {/* Main Content Area - Maximized Width */}
      <main className="flex-1 flex flex-col min-w-0 relative z-10 bg-white shadow-[-1px_0_0_rgba(0,0,0,0.05)]">
        
        {/* Header - Clean Monochrome */}
        <header className="h-[60px] flex items-center justify-between px-6 border-b border-slate-100 bg-white sticky top-0 z-20">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-1.5 hover:bg-slate-50 rounded border border-transparent hover:border-slate-200 text-slate-400 transition-all"
            >
              <Menu size={16} />
            </button>
            <div className="flex flex-col">
              <h2 className="text-xs font-bold text-slate-800 tracking-wide uppercase flex items-center gap-2">
                Agentic Architecture Alignment
                <span className="bg-slate-100 text-slate-500 text-[9px] px-1.5 py-0.5 rounded border border-slate-200 font-bold uppercase">PRO</span>
              </h2>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-2.5 py-1 bg-slate-50 border border-slate-200 rounded text-[10px] font-bold text-slate-600">
               <div className="w-1.5 h-1.5 bg-slate-900 rounded-full animate-pulse"></div>
               SYSTEM ACTIVE
            </div>
          </div>
        </header>

        {/* Messages Stream - WIDER WIDTH */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 sm:p-10 scroll-smooth">
          <div className="max-w-[1100px] mx-auto space-y-12 pb-48">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-6 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                <div className={`w-9 h-9 rounded flex-shrink-0 flex items-center justify-center border mt-1 shadow-sm ${
                  msg.role === "ai" ? "bg-slate-900 border-slate-900 text-white" : "bg-white border-slate-200 text-slate-900"
                }`}>
                  {msg.role === "ai" ? <Cpu size={18} /> : <User size={18} />}
                </div>

                <div className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"} flex-1 space-y-3`}>
                  <div className={`text-[15px] leading-relaxed w-full ${
                    msg.role === "user" 
                      ? "bg-slate-50 text-slate-900 border border-slate-200 rounded-lg px-6 py-4 inline-block w-auto max-w-[80%]" 
                      : "bg-white text-slate-800 rounded-lg p-0"
                  }`}>
                    
                    {!msg.structuredData && (
                      <div className="whitespace-pre-wrap font-medium">
                        {msg.content.split('\n').map((line: string, i: number) => (
                          <div key={i} className="mb-2">
                            {line.split('**').map((part, j) => j % 2 !== 0 ? <strong key={j} className="text-slate-900 font-extrabold">{part}</strong> : part)}
                          </div>
                        ))}
                      </div>
                    )}

                    {msg.structuredData && (
                      <div className="space-y-10 w-full animate-in fade-in duration-700">
                        {msg.structuredData.status === 'error' && (
                          <div className="p-4 bg-slate-50 text-slate-700 border-l-4 border-slate-900 rounded-r flex items-center gap-3">
                            <AlertCircle size={16} />
                            <span>{msg.structuredData.message}</span>
                          </div>
                        )}

                        {/* Clarification - Distinct but Professional */}
                        {msg.structuredData.final_resolution?.includes("Clarification Needed") && (
                          <div className="p-8 border-2 border-slate-900 rounded-xl bg-slate-50/50">
                             <div className="flex items-center gap-3 mb-4">
                               <div className="p-2 bg-slate-900 rounded text-white"><Info size={16}/></div>
                               <h4 className="font-bold text-slate-900 text-lg uppercase tracking-tight">Clarification Protocol</h4>
                             </div>
                             <p className="text-slate-700 text-base leading-relaxed font-medium">
                               {msg.structuredData.final_resolution.replace('🤔 **Clarification Needed:** ', '').replace('\n\n_Please reply with more details to proceed._', '')}
                             </p>
                             <div className="mt-6 flex items-center gap-2 text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                               <div className="w-1.5 h-1.5 bg-slate-300 rounded-full"></div>
                               Awaiting user specification
                             </div>
                          </div>
                        )}

                        {!msg.structuredData.final_resolution?.includes("Clarification Needed") && msg.structuredData.status === 'success' && (
                          <>
                            {/* Section 1: Analysis */}
                            {msg.structuredData.context_analysis && (
                               <div className="space-y-4">
                                 <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
                                   <Search size={14} className="text-slate-300" />
                                   Architectural Context Analysis
                                 </h4>
                                 <div className="text-slate-600 text-[15px] leading-[1.7] pl-6 border-l border-slate-100">
                                   {msg.structuredData.context_analysis}
                                 </div>
                               </div>
                            )}

                            {/* Section 2: Resolution - Main Focus */}
                            {msg.structuredData.final_resolution && (
                               <div className="space-y-4 bg-slate-50 border border-slate-200 rounded-xl p-8 shadow-sm">
                                 <h4 className="text-[11px] font-black text-slate-900 uppercase tracking-[0.2em] flex items-center gap-2">
                                   <CheckCircle2 size={14} className="text-slate-900" />
                                   Technical Resolution
                                 </h4>
                                 <div className="text-slate-900 text-lg leading-relaxed font-semibold">
                                   {msg.structuredData.final_resolution}
                                 </div>
                               </div>
                            )}

                            {/* Mappings Table-like layout */}
                            {msg.structuredData.answer?.length > 0 && (
                               <div className="space-y-6 pt-4">
                                 <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em]">
                                   Ontology Mappings & Traceability
                                 </h4>
                                 <div className="grid gap-4">
                                   {msg.structuredData.answer.map((m: any, i: number) => (
                                      <div key={i} className="group border border-slate-100 hover:border-slate-300 rounded-lg p-6 transition-all bg-white shadow-[0_2px_8px_rgba(0,0,0,0.02)]">
                                         <div className="flex items-center justify-between mb-4 pb-4 border-b border-slate-50">
                                           <div className="flex items-center gap-3">
                                              <span className="font-bold text-slate-900 text-base">{m.devops_concept}</span>
                                              <ArrowRight size={14} className="text-slate-300" />
                                              <span className="font-bold text-slate-500 text-base italic">{m.msa_concept}</span>
                                           </div>
                                           <span className="text-[10px] font-bold text-slate-400 border border-slate-100 px-2 py-0.5 rounded bg-slate-50 uppercase tracking-wider">
                                             {m.taxonomy_category}
                                           </span>
                                         </div>
                                         <p className="text-slate-600 text-sm leading-relaxed mb-4">{m.explanation || m.justification}</p>
                                           
                                         {/* UPDATED: Interactive Source Buttons */}
                                         <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 flex-wrap">
                                            <FileText size={12} className="flex-shrink-0" />
                                            <span className="mr-1 tracking-widest uppercase">Sources:</span>
                                            {m.sources && m.sources.length > 0 ? (
                                              m.sources.map((src: string, srcIdx: number) => (
                                                <button
                                                  key={srcIdx}
                                                  // Triggers an automatic follow-up query when clicked!
                                                  onClick={() => handleSend(undefined, `Can you explain the architectural significance of the retrieved document ${src} in detail?`)}
                                                  className="hover:text-slate-900 hover:bg-slate-100 cursor-pointer border border-slate-200 hover:border-slate-400 px-2.5 py-1 rounded-md bg-slate-50 transition-all flex items-center gap-1.5 active:scale-95 shadow-sm"
                                                  title="Click to ask MARCO to explain this specific document"
                                                >
                                                  {src}
                                                  <Sparkles size={10} className="text-slate-400 group-hover/btn:text-slate-600" />
                                                </button>
                                              ))
                                            ) : (
                                              <span className="px-2 py-0.5 bg-slate-50 border border-slate-100 rounded">SYSTEM KB</span>
                                            )}
                                         </div>

                                      </div>
                                   ))}
                                 </div>
                               </div>
                            )}

                            {/* Suggestions */}
                            {msg.structuredData.suggested_next_steps?.length > 0 && (
                               <div className="pt-8 space-y-4">
                                 <h4 className="text-[10px] font-black text-slate-300 uppercase tracking-[0.3em]">Next Steps</h4>
                                 <div className="flex flex-wrap gap-2">
                                   {msg.structuredData.suggested_next_steps.map((step: string, i: number) => (
                                     <button 
                                       key={i}
                                       onClick={() => handleSend(undefined, step)}
                                       className="text-left px-4 py-2 bg-white border border-slate-200 hover:border-slate-900 rounded-md text-[13px] font-bold text-slate-700 transition-all cursor-pointer flex items-center gap-2 active:scale-95"
                                     >
                                       {step}
                                       <ArrowRight size={12} className="opacity-0 group-hover:opacity-100" />
                                     </button>
                                   ))}
                                 </div>
                               </div>
                            )}

                            {/* Context Chunks - Minimalist Details */}
                            {msg.structuredData.retrieved_chunks?.length > 0 && (
                               <details className="w-full mt-6 group border-t border-slate-100 pt-6">
                                 <summary className="text-[10px] font-bold text-slate-400 cursor-pointer hover:text-slate-900 uppercase tracking-[0.2em] outline-none flex items-center gap-2 transition-colors">
                                   <Terminal size={12} />
                                   Retrieved Context Trace ({msg.structuredData.retrieved_chunks.filter((c:any) => c.accepted).length})
                                 </summary>
                                 <div className="mt-6 space-y-2">
                                   {msg.structuredData.retrieved_chunks.filter((c:any) => c.accepted).map((chunk: any, i: number) => (
                                     <div key={i} className="bg-slate-50/50 p-4 rounded border border-slate-100 flex items-start gap-4">
                                       <span className="text-[9px] font-mono text-slate-400 mt-1">#{(i+1).toString().padStart(2,'0')}</span>
                                       <div>
                                         <p className="text-xs font-mono text-slate-600 leading-relaxed italic">{chunk.definition}</p>
                                         <p className="text-[9px] font-bold text-slate-400 mt-2 uppercase tracking-widest">{chunk.reference_name || 'KB CORE'}</p>
                                       </div>
                                     </div>
                                   ))}
                                 </div>
                               </details>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Reasoning Trace */}
                  {msg.reasoning && msg.reasoning.length > 0 && (
                    <details className="w-full max-w-2xl mt-2 group">
                      <summary className="text-[10px] font-bold text-slate-400 cursor-pointer hover:text-slate-900 uppercase tracking-widest outline-none inline-block border-b border-transparent hover:border-slate-200">
                        Execution Trace
                      </summary>
                      <div className="mt-3 p-4 bg-slate-50 border border-slate-200 rounded space-y-2 shadow-inner">
                        {msg.reasoning.map((step: string, i: number) => (
                          <div key={i} className="text-[11px] font-mono text-slate-500 flex gap-3">
                            <span className="text-slate-300">→</span>
                            <span className="leading-relaxed">{step}</span>
                          </div>
                        ))}
                      </div>
                    </details>
                  )}

                  <span suppressHydrationWarning className="text-[10px] font-bold text-slate-300 px-2 mt-1 tabular-nums">
                    {msg.time} • LOGGED
                  </span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-6 animate-in fade-in">
                <div className="w-9 h-9 rounded bg-slate-100 border border-slate-200 flex-shrink-0 flex items-center justify-center mt-1">
                   <Cpu size={18} className="text-slate-400 animate-pulse" />
                </div>
                <div className="bg-white px-6 py-5 rounded border border-slate-100 shadow-sm flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-900 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-900 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-900 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input Area - Maximized Width */}
        <div className="absolute bottom-0 left-0 right-0 px-6 pb-10 bg-gradient-to-t from-white via-white to-transparent pt-20 pointer-events-none">
          <div className="max-w-[1100px] mx-auto pointer-events-auto flex flex-col gap-4">
            
            {selectedFile && (
              <div className="mx-4 flex items-center justify-between bg-slate-900 text-white pl-2 pr-4 py-2 rounded text-xs animate-in slide-in-from-bottom-2">
                <div className="flex items-center gap-3 font-bold">
                  {previewUrl ? (
                    <img src={previewUrl} alt="Preview" className="w-8 h-8 object-cover rounded-sm" />
                  ) : (
                    <FileText size={14} className="ml-2" />
                  )}
                  <span className="uppercase tracking-widest">{selectedFile.name}</span>
                </div>
                <button onClick={() => setSelectedFile(null)} className="p-1 hover:bg-slate-800 rounded transition-colors">
                  <X size={14} />
                </button>
              </div>
            )}

            <div className="bg-white border-2 border-slate-900 shadow-[8px_8px_0_rgba(15,23,42,0.1)] transition-all duration-300 group focus-within:shadow-[12px_12px_0_rgba(15,23,42,0.1)]">
              <form onSubmit={handleSend} className="flex items-end">
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={onFileChange} 
                  className="hidden" 
                  accept=".png,.jpg,.jpeg,.pdf,.yml,.yaml,.tf"
                />
                <button 
                  type="button" 
                  onClick={() => fileInputRef.current?.click()}
                  className={`p-5 transition-all ${selectedFile ? "text-slate-900 bg-slate-100" : "text-slate-400 hover:text-slate-900"}`}
                >
                  <Paperclip size={20} />
                </button>
                
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                  placeholder="Analyze architectural alignment..."
                  className="flex-1 max-h-48 py-5 px-2 bg-transparent border-none focus:ring-0 resize-none text-slate-900 text-base font-medium placeholder-slate-300"
                  rows={1}
                />
                
                <button 
                  type="submit" 
                  disabled={!input.trim() && !selectedFile}
                  className={`p-5 transition-all ${input.trim() || selectedFile ? "bg-slate-900 text-white hover:bg-black" : "bg-slate-50 text-slate-300 cursor-not-allowed"}`}
                >
                  <Send size={20} strokeWidth={3} />
                </button>
              </form>
            </div>
            <div className="flex justify-between items-center px-1">
              <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">
                Ontology Research Terminal v1.0
              </p>
              <div className="flex gap-4">
                 <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Grounded</span>
                 <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Verifiable</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function SidebarItem({ icon, label, active = false }: { icon: React.ReactNode, label: string, active?: boolean }) {
  return (
    <button className={`w-full flex items-center justify-between group rounded px-3 py-2.5 text-[11px] font-bold uppercase tracking-wider transition-all ${
      active ? "bg-slate-100 text-slate-900 shadow-sm" : "text-slate-400 hover:bg-slate-50 hover:text-slate-600"
    }`}>
      <div className="flex items-center gap-3">
        <span className={`${active ? "text-slate-900" : "text-slate-300 group-hover:text-slate-400"} transition-colors`}>{icon}</span>
        {label}
      </div>
      {active && <div className="w-1 h-1 rounded-full bg-slate-900 mr-1"></div>}
    </button>
  );
}
