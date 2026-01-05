"use client";

import { useState, useEffect, useRef } from "react";

export default function Home() {
    const [inputMode, setInputMode] = useState<"member" | "urls">("member");
    const [memberId, setMemberId] = useState("3902132645");
    const [urls, setUrls] = useState("");
    const [maxPages, setMaxPages] = useState(10);
    const [isRunning, setIsRunning] = useState(false);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState("");
    const [results, setResults] = useState<any>(null);
    const [isTauriMode, setIsTauriMode] = useState(false);

    // 리스너 관리용 Ref
    const unlistenLogRef = useRef<(() => void) | null>(null);
    const unlistenCompleteRef = useRef<(() => void) | null>(null);

    // 컴포넌트 언마운트 시 리스너 정리
    useEffect(() => {
        return () => {
            if (unlistenLogRef.current) unlistenLogRef.current();
            if (unlistenCompleteRef.current) unlistenCompleteRef.current();
        };
    }, []);

    useEffect(() => {
        // Tauri 환경 감지 - API import로 직접 확인
        const checkTauri = async () => {
            try {
                const { invoke } = await import('@tauri-apps/api/core');
                console.log('✅ Tauri mode detected - API imported successfully');
                console.log('✅ invoke function:', typeof invoke);
                setIsTauriMode(true);
            } catch (e) {
                console.log('❌ Not in Tauri mode - API import failed:', e);
                setIsTauriMode(false);
            }
        };
        checkTauri();
    }, []);

    const handleStart = async () => {
        if (isRunning) return;

        // 기존 리스너 정리
        if (unlistenLogRef.current) {
            unlistenLogRef.current();
            unlistenLogRef.current = null;
        }
        if (unlistenCompleteRef.current) {
            unlistenCompleteRef.current();
            unlistenCompleteRef.current = null;
        }

        setIsRunning(true);
        setProgress(0);
        setStatus("스크래핑 준비 중...");
        setResults(null);

        try {
            console.log('🔍 isTauriMode:', isTauriMode);
            if (isTauriMode) {
                console.log('📞 Importing Tauri APIs...');
                const { invoke } = await import('@tauri-apps/api/core');
                const { listen } = await import('@tauri-apps/api/event');

                // 로그 리스너
                console.log('👂 Setting up event listeners...');
                unlistenLogRef.current = await listen<string>('scraping-log', (event) => {
                    const line = event.payload;
                    console.log('📨 Received log:', line);
                    try {
                        const json = JSON.parse(line);
                        if (json.progress !== undefined) {
                            setProgress(json.progress);
                            setStatus(json.status || "처리 중...");
                        }
                        if (json.saved_files) {
                            setResults(json);
                        }
                    } catch (e) {
                        console.log("Text log:", line);
                    }
                });

                // 완료 리스너
                unlistenCompleteRef.current = await listen('scraping-complete', () => {
                    console.log('✅ Scraping complete event received');
                    setProgress(100);
                    setStatus("완료!");
                    setIsRunning(false);
                });

                const mode = inputMode;
                const data = inputMode === "member" ? memberId : JSON.stringify(urls.split('\n').filter(u => u.trim()));

                console.log('🚀 Invoking start_scraping with:', { mode, data, maxPages: inputMode === "member" ? maxPages : undefined });
                setStatus("스크래퍼 실행...");

                await invoke("start_scraping", {
                    mode,
                    data,
                    maxPages: inputMode === "member" ? maxPages : undefined
                });
                console.log('✅ start_scraping invoked successfully');

            } else {
                // 웹 환경: 시뮬레이션
                setStatus("⚠️ Tauri 데스크톱 앱에서만 사용 가능합니다");
                await new Promise(resolve => setTimeout(resolve, 1000));
                setIsRunning(false);
            }
        } catch (error: any) {
            console.error(error);
            setStatus("❌ 에러 발생: " + error.toString());
            setIsRunning(false);
        }
    };

    const openFile = async (path: string) => {
        try {
            if (isTauriMode) {
                const { invoke } = await import('@tauri-apps/api/core');
                await invoke('open_explorer', { path });
            }
        } catch (e) {
            console.error(e);
            alert("파일을 여는데 실패했습니다: " + e);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">
                        📊 FM Korea 투자 패턴 분석기
                    </h1>
                    <p className="text-gray-400">
                        특정 작성자의 게시물을 수집하고 투자 패턴을 분석합니다
                    </p>
                </div>

                {/* Main Card */}
                <div className="bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700 p-6 shadow-2xl">
                    {/* Input Mode Tabs */}
                    <div className="flex gap-2 mb-6">
                        <button
                            onClick={() => setInputMode("member")}
                            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${inputMode === "member"
                                ? "bg-blue-600 text-white shadow-lg shadow-blue-500/50"
                                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                                }`}
                        >
                            회원번호로 검색
                        </button>
                        <button
                            onClick={() => setInputMode("urls")}
                            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${inputMode === "urls"
                                ? "bg-blue-600 text-white shadow-lg shadow-blue-500/50"
                                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                                }`}
                        >
                            직접 URL 입력
                        </button>
                    </div>

                    {/* Input Area */}
                    {inputMode === "member" ? (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    회원번호
                                </label>
                                <input
                                    type="text"
                                    value={memberId}
                                    onChange={(e) => setMemberId(e.target.value)}
                                    placeholder="예: 3902132645"
                                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    최대 페이지 수
                                </label>
                                <input
                                    type="number"
                                    value={maxPages}
                                    onChange={(e) => setMaxPages(parseInt(e.target.value))}
                                    min="1"
                                    max="50"
                                    className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    ) : (
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                게시물 URL (한 줄에 하나씩)
                            </label>
                            <textarea
                                value={urls}
                                onChange={(e) => setUrls(e.target.value)}
                                placeholder="https://www.fmkorea.com/..."
                                rows={8}
                                className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                            />
                        </div>
                    )}

                    {/* Start Button */}
                    <button
                        onClick={handleStart}
                        disabled={isRunning}
                        className={`w-full mt-6 py-4 rounded-lg font-bold text-lg transition-all ${isRunning
                            ? "bg-gray-600 text-gray-400 cursor-not-allowed"
                            : "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-500 hover:to-purple-500 shadow-lg shadow-blue-500/50"
                            }`}
                    >
                        {isRunning ? "실행 중..." : "🚀 분석 시작"}
                    </button>

                    {/* Progress */}
                    {isRunning && (
                        <div className="mt-6 space-y-3">
                            <div className="flex justify-between text-sm text-gray-400">
                                <span>{status}</span>
                                <span>{progress}%</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                                <div
                                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-full transition-all duration-300 rounded-full"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>
                        </div>
                    )}

                    {/* Results */}
                    {results && (
                        <div className="mt-6 p-6 bg-gradient-to-br from-green-900/40 to-emerald-900/40 rounded-2xl border border-green-700/30 backdrop-blur-md shadow-xl">
                            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                                ✅ 분석 완료!
                            </h3>

                            <div className="space-y-4">
                                <div className="flex justify-between items-center text-gray-300 bg-gray-800/50 p-3 rounded-lg">
                                    <span>수집된 게시물</span>
                                    <span className="font-mono font-bold text-white text-lg">{results.total_files || 0}개</span>
                                </div>

                                {results.notebooklm_files && results.notebooklm_files.length > 0 && (
                                    <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-700">
                                        <p className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">NotebookLM용 Markdown</p>
                                        <div className="space-y-2">
                                            {results.notebooklm_files.map((file: string, idx: number) => (
                                                <button
                                                    key={idx}
                                                    onClick={() => openFile(file)}
                                                    className="w-full text-left flex items-center gap-3 text-green-400 hover:text-green-300 hover:bg-green-900/20 p-3 rounded-lg transition-all border border-transparent hover:border-green-800/50 group"
                                                >
                                                    <span className="text-2xl">📝</span>
                                                    <span className="flex-1 font-mono text-sm break-all truncate">{file.split('\\').pop()?.split('/').pop()}</span>
                                                    <span className="text-xs text-gray-500 group-hover:text-green-400 transition-colors">열기 ↗</span>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {results.guide_file && (
                                    <button
                                        onClick={() => openFile(results.guide_file)}
                                        className="w-full text-left flex items-center gap-3 text-blue-400 hover:text-blue-300 bg-gray-800/50 hover:bg-blue-900/20 p-3 rounded-lg transition-all border border-gray-700 hover:border-blue-800/50 group"
                                    >
                                        <span className="text-2xl">📖</span>
                                        <span className="flex-1 font-mono text-sm">분석_가이드.md</span>
                                        <span className="text-xs text-gray-500 group-hover:text-blue-400 transition-colors">열기 ↗</span>
                                    </button>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="text-center mt-6 text-gray-500 text-sm">
                    <p>⚠️ 개인적인 학습 및 연구 목적으로만 사용하세요</p>
                </div>
            </div>
        </div>
    );
}
