"use client";

import { useState } from "react";

export default function Home() {
    const [inputMode, setInputMode] = useState<"member" | "urls">("member");
    const [memberId, setMemberId] = useState("3902132645");
    const [urls, setUrls] = useState("");
    const [maxPages, setMaxPages] = useState(10);
    const [isRunning, setIsRunning] = useState(false);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState("");
    const [results, setResults] = useState<any>(null);

    const handleStart = async () => {
        setIsRunning(true);
        setProgress(0);
        setStatus("스크래핑 시작...");

        try {
            // TODO: Tauri 커맨드 호출
            // const result = await invoke("start_scraping", { ... });

            // 임시 시뮬레이션
            for (let i = 0; i <= 100; i += 10) {
                await new Promise(resolve => setTimeout(resolve, 500));
                setProgress(i);
                setStatus(`진행 중... ${i}%`);
            }

            setStatus("완료!");
        } catch (error) {
            console.error(error);
            setStatus("에러 발생: " + error);
        } finally {
            setIsRunning(false);
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
                        <div className="mt-6 p-4 bg-gray-700/50 rounded-lg">
                            <h3 className="text-lg font-bold text-white mb-2">분석 결과</h3>
                            <pre className="text-sm text-gray-300 overflow-auto">
                                {JSON.stringify(results, null, 2)}
                            </pre>
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
